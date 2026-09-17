from datetime import date, time, datetime
from sqlalchemy.orm import Session
from app.database import SessionLocal
from ..services.appointment_service import (
    get_available_slots,
    get_nearby_slots,
    book_appointment,
    get_user_appointments,
    get_user_appointment,
    cancel_appointment,
    reschedule_appointment,
    is_past_datetime,
)

from ..models import Service

def get_services():
    """
    Fetch all active salon services from the database.
    """

    db = SessionLocal()

    try:
        services = (
            db.query(Service)
            .filter(Service.is_active == True)
            .order_by(Service.id)
            .all()
        )

        return {
            "success": True,
            "services": [
                {
                    "id": service.id,
                    "name": service.name,
                    "duration_minutes": service.duration_minutes,
                    "price": float(service.price),
                }
                for service in services
            ],
        }

    finally:
        db.close()
# ---------------------------------------------------------
# FIND SERVICE
# ---------------------------------------------------------


def find_service(db: Session, service_name: str):
    """
    Find an active salon service using a normalized service name.

    Matching ignores:
    - Uppercase/lowercase differences
    - Extra spaces before or after the service name
    """

    normalized_name = service_name.strip().lower()

    services = db.query(Service).filter(Service.is_active.is_(True)).all()

    for service in services:
        if service.name.strip().lower() == normalized_name:
            return service

    return None


# ---------------------------------------------------------
# CHECK AVAILABILITY
# ---------------------------------------------------------


def check_availability(
    db: Session,
    appointment_date: date,
    service_name: str,
):
    """
    Check available appointment slots for a service on a given date.
    """

    # Reject past dates
    if is_past_datetime(appointment_date, time.max):
        return {
            "success": False,
            "message": "Appointments cannot be booked for dates in the past.",
        }

    # Find the requested service
    service = find_service(db, service_name)

    if not service:
        return {
            "success": False,
            "message": f"Service '{service_name}' is not available.",
        }

    slots = get_available_slots(
        db=db,
        appointment_date=appointment_date,
        service_duration=service.duration_minutes,
    )

    return {
        "success": True,
        "service": service.name,
        "date": str(appointment_date),
        "available_slots": [slot.strftime("%H:%M") for slot in slots],
    }


# ---------------------------------------------------------
# FIND NEARBY SLOTS
# ---------------------------------------------------------


def find_nearby_slots(
    db: Session,
    appointment_date: date,
    requested_time: time,
    service_name: str,
):
    """
    Find nearby available slots for a requested service and time.
    """

    # Reject past date/time
    if is_past_datetime(appointment_date, requested_time):
        return {
            "success": False,
            "message": (
                "Appointments cannot be checked for " "dates and times in the past."
            ),
        }

    # Find the requested service
    service = find_service(db, service_name)

    if not service:
        return {
            "success": False,
            "message": f"Service '{service_name}' is not available.",
        }

    slots = get_nearby_slots(
        db=db,
        appointment_date=appointment_date,
        requested_time=requested_time,
        service_duration=service.duration_minutes,
    )

    return {
        "success": True,
        "service": service.name,
        "date": str(appointment_date),
        "requested_time": requested_time.strftime("%H:%M"),
        "nearby_slots": [slot.strftime("%H:%M") for slot in slots],
    }


# ---------------------------------------------------------
# CREATE BOOKING
# ---------------------------------------------------------


def create_booking(
    db: Session,
    user_id: int,
    appointment_date: date,
    appointment_time: time,
    service_name: str,
):
    """
    Create a new appointment for the logged-in user.
    """

    # Find the requested service
    service = find_service(db, service_name)

    if not service:
        return {
            "success": False,
            "message": f"Service '{service_name}' is not available.",
        }

    appointment = book_appointment(
        db=db,
        user_id=user_id,
        service_id=service.id,
        appointment_date=appointment_date,
        appointment_time=appointment_time,
    )

    # Handle validation errors
    if isinstance(appointment, dict):
        return appointment

    # Handle unavailable slots
    if appointment is None:
        return {
            "success": False,
            "message": "Sorry, that slot is not available.",
        }

    return {
        "success": True,
        "message": "Appointment booked successfully.",
        "appointment": {
            "appointment_id": appointment.id,
            "service": service.name,
            "date": str(appointment.appointment_date),
            "time": appointment.appointment_time.strftime("%H:%M"),
            "status": appointment.status,
        },
    }


# ---------------------------------------------------------
# RESCHEDULE APPOINTMENT
# ---------------------------------------------------------


def reschedule_my_appointment(
    db: Session,
    user_id: int,
    appointment_id: int,
    new_date: date,
    new_time: time,
):
    """
    Reschedule an existing appointment.
    """

    appointment = reschedule_appointment(
        db=db,
        user_id=user_id,
        appointment_id=appointment_id,
        new_date=new_date,
        new_time=new_time,
    )

    # Validation error
    if isinstance(appointment, dict):
        return appointment

    if appointment is None:
        return {
            "success": False,
            "message": "Appointment not found.",
        }

    if appointment is False:
        return {
            "success": False,
            "message": "The new time slot is unavailable.",
        }

    service = db.query(Service).filter(Service.id == appointment.service_id).first()

    return {
        "success": True,
        "message": "Appointment rescheduled successfully.",
        "appointment": {
            "appointment_id": appointment.id,
            "service": service.name if service else "Unknown service",
            "date": str(appointment.appointment_date),
            "time": appointment.appointment_time.strftime("%H:%M"),
            "status": appointment.status,
        },
    }


# ---------------------------------------------------------
# GET ALL USER APPOINTMENTS
# ---------------------------------------------------------


def get_my_appointments(
    db: Session,
    user_id: int,
):
    """
    Return the user's appointments separated into upcoming and past appointments.
    Cancelled appointments are excluded from both lists.
    """

    appointments = get_user_appointments(
        db=db,
        user_id=user_id,
    )

    upcoming_appointments = []
    past_appointments = []

    today = date.today()

    for appointment in appointments:

        # Skip cancelled appointments
        if appointment.status.lower() == "cancelled":
            continue

        service = (
            db.query(Service)
            .filter(Service.id == appointment.service_id)
            .first()
        )

        appointment_data = {
            "appointment_id": appointment.id,
            "service": service.name if service else "Unknown service",
            "date": str(appointment.appointment_date),
            "time": appointment.appointment_time.strftime("%H:%M"),
            "status": appointment.status,
        }

        # Compare appointment date with today's date
        if appointment.appointment_date >= today:
            upcoming_appointments.append(appointment_data)
        else:
            past_appointments.append(appointment_data)

    # Sort appointments chronologically
    upcoming_appointments.sort(
        key=lambda appointment: (
            appointment["date"],
            appointment["time"],
        )
    )

    past_appointments.sort(
        key=lambda appointment: (
            appointment["date"],
            appointment["time"],
        ),
        reverse=True,
    )

    return {
        "success": True,
        "upcoming_appointments": upcoming_appointments,
        "past_appointments": past_appointments,
    }
# ---------------------------------------------------------
# GET ONE USER APPOINTMENT
# ---------------------------------------------------------


def get_my_appointment(
    db: Session,
    user_id: int,
    appointment_id: int,
):
    """
    Return one appointment belonging to the current user.
    """

    appointment = get_user_appointment(
        db=db,
        user_id=user_id,
        appointment_id=appointment_id,
    )

    if not appointment:
        return {
            "success": False,
            "message": "Appointment not found.",
        }

    service = db.query(Service).filter(Service.id == appointment.service_id).first()

    return {
        "success": True,
        "appointment": {
            "appointment_id": appointment.id,
            "service": service.name if service else "Unknown service",
            "date": str(appointment.appointment_date),
            "time": appointment.appointment_time.strftime("%H:%M"),
            "status": appointment.status,
        },
    }


# ---------------------------------------------------------
# CANCEL APPOINTMENT
# ---------------------------------------------------------


def cancel_my_appointment(
    db: Session,
    user_id: int,
    appointment_id: int,
):
    """
    Cancel an appointment only if it belongs to the current user.
    """

    appointment = cancel_appointment(
        db=db,
        appointment_id=appointment_id,
        user_id=user_id,
    )

    if not appointment:
        return {
            "success": False,
            "message": (
                "Appointment not found, "
                "does not belong to this user, "
                "or is already cancelled."
            ),
        }

    return {
        "success": True,
        "message": "Appointment cancelled successfully.",
        "appointment_id": appointment.id,
        "status": appointment.status,
    }
# ---------------------------------------------------------
# GET ALL SERVICES
# ---------------------------------------------------------

def get_services(db: Session):
    """
    Return all active salon services with their prices and durations.
    """

    services = (
        db.query(Service)
        .filter(Service.is_active.is_(True))
        .order_by(Service.id)
        .all()
    )

    service_list = []

    for service in services:
        service_list.append(
            {
                "service_id": service.id,
                "name": service.name,
                "duration_minutes": service.duration_minutes,
                "price": service.price,
            }
        )

    return {
        "success": True,
        "services": service_list,
    }
