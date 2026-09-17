from sqlalchemy.orm import Session
from datetime import date, time, datetime, timedelta

from ..models import Appointment, Service

# ---------------------------------------------------------
# DATE AND TIME VALIDATION
# ---------------------------------------------------------


def validate_appointment_date(appointment_date: date):
    """
    Validate that the appointment date is today or in the future.
    """

    today = date.today()

    if appointment_date < today:
        return {
            "success": False,
            "message": "You cannot book an appointment in the past.",
        }

    return {
        "success": True,
        "message": "Date is valid.",
    }


def is_past_datetime(appointment_date: date, appointment_time: time):
    requested_datetime = datetime.combine(
        appointment_date,
        appointment_time,
    )

    return requested_datetime < datetime.now()


def is_within_working_hours(
    appointment_time: time,
    service_duration: int,
):
    salon_opening_time = time(10, 0)
    salon_closing_time = time(18, 0)

    today = date.today()

    appointment_datetime = datetime.combine(
        today,
        appointment_time,
    )

    opening_datetime = datetime.combine(
        today,
        salon_opening_time,
    )

    closing_datetime = datetime.combine(
        today,
        salon_closing_time,
    )

    appointment_end_datetime = appointment_datetime + timedelta(
        minutes=service_duration
    )

    return (
        appointment_datetime >= opening_datetime
        and appointment_end_datetime <= closing_datetime
    )


# ---------------------------------------------------------
# CHECK IF A SLOT IS AVAILABLE
# ---------------------------------------------------------


def is_slot_available(
    db: Session,
    appointment_date: date,
    appointment_time: time,
    service_duration: int,
):
    requested_start = datetime.combine(
        appointment_date,
        appointment_time,
    )

    requested_end = requested_start + timedelta(minutes=service_duration)

    existing_appointments = (
        db.query(Appointment)
        .filter(
            Appointment.appointment_date == appointment_date,
            Appointment.status == "booked",
        )
        .all()
    )

    for appointment in existing_appointments:

        existing_service = (
            db.query(Service).filter(Service.id == appointment.service_id).first()
        )

        if not existing_service:
            continue

        existing_start = datetime.combine(
            appointment.appointment_date,
            appointment.appointment_time,
        )

        existing_end = existing_start + timedelta(
            minutes=existing_service.duration_minutes
        )

        if requested_start < existing_end and requested_end > existing_start:
            return False

    return True


# ---------------------------------------------------------
# BOOK APPOINTMENT
# ---------------------------------------------------------


def book_appointment(
    db: Session,
    user_id: int,
    service_id: int,
    appointment_date: date,
    appointment_time: time,
):
    # Reject appointments in the past
    # Validate appointment date
    date_validation = validate_appointment_date(appointment_date)

    if not date_validation["success"]:
        return date_validation

    # Reject appointments in the past
    if is_past_datetime(appointment_date, appointment_time):
        return {
            "success": False,
            "message": "You cannot book an appointment in the past.",
        }
    # Get the selected service
    service = (
        db.query(Service)
        .filter(
            Service.id == service_id,
            Service.is_active == True,
        )
        .first()
    )

    if not service:
        return None

    # Check working hours
    if not is_within_working_hours(
        appointment_time=appointment_time,
        service_duration=service.duration_minutes,
    ):
        return {
            "success": False,
            "message": (
                "Appointments must be scheduled between " "10:00 AM and 6:00 PM."
            ),
        }

    # Check whether the requested time is available
    if not is_slot_available(
        db=db,
        appointment_date=appointment_date,
        appointment_time=appointment_time,
        service_duration=service.duration_minutes,
    ):
        return None

    appointment = Appointment(
        user_id=user_id,
        service_id=service_id,
        appointment_date=appointment_date,
        appointment_time=appointment_time,
        status="booked",
    )

    db.add(appointment)
    db.commit()
    db.refresh(appointment)

    return appointment


# ---------------------------------------------------------
# GET AVAILABLE SLOTS
# ---------------------------------------------------------


def get_available_slots(
    db: Session,
    appointment_date: date,
    service_duration: int = 30,
    start_hour: int = 10,
    end_hour: int = 18,
    slot_duration: int = 30,
):
    available_slots = []

    current_time = datetime.combine(
        appointment_date,
        time(start_hour, 0),
    )

    end_time = datetime.combine(
        appointment_date,
        time(end_hour, 0),
    )

    while current_time < end_time:

        current_slot = current_time.time()

        service_end_time = current_time + timedelta(minutes=service_duration)

        if service_end_time > end_time:
            break

        if is_slot_available(
            db=db,
            appointment_date=appointment_date,
            appointment_time=current_slot,
            service_duration=service_duration,
        ):
            available_slots.append(current_slot)

        current_time += timedelta(minutes=slot_duration)

    return available_slots


# ---------------------------------------------------------
# GET ONE USER APPOINTMENT
# ---------------------------------------------------------


def get_user_appointment(
    db: Session,
    user_id: int,
    appointment_id: int,
):
    appointment = (
        db.query(Appointment)
        .filter(
            Appointment.id == appointment_id,
            Appointment.user_id == user_id,
            Appointment.status == "booked",
        )
        .first()
    )

    return appointment


# ---------------------------------------------------------
# RESCHEDULE APPOINTMENT
# ---------------------------------------------------------


def reschedule_appointment(
    db: Session,
    user_id: int,
    appointment_id: int,
    new_date: date,
    new_time: time,
):
    # Reject past dates and times
    if is_past_datetime(new_date, new_time):
        return {
            "success": False,
            "message": ("You cannot reschedule an appointment " "to the past."),
        }

    # Find the appointment belonging to the current user
    appointment = (
        db.query(Appointment)
        .filter(
            Appointment.id == appointment_id,
            Appointment.user_id == user_id,
            Appointment.status == "booked",
        )
        .first()
    )

    if not appointment:
        return None

    # Get the service to know its duration
    service = db.query(Service).filter(Service.id == appointment.service_id).first()

    if not service:
        return None

    # Check working hours
    if not is_within_working_hours(
        appointment_time=new_time,
        service_duration=service.duration_minutes,
    ):
        return {
            "success": False,
            "message": (
                "Appointments must be scheduled between " "10:00 AM and 6:00 PM."
            ),
        }

    # Check whether the new slot is available
    if not is_slot_available(
        db=db,
        appointment_date=new_date,
        appointment_time=new_time,
        service_duration=service.duration_minutes,
    ):
        return False

    # Update the existing appointment
    appointment.appointment_date = new_date
    appointment.appointment_time = new_time

    db.commit()
    db.refresh(appointment)

    return appointment


# ---------------------------------------------------------
# CANCEL APPOINTMENT
# ---------------------------------------------------------


def cancel_appointment(
    db: Session,
    appointment_id: int,
    user_id: int,
):
    appointment = (
        db.query(Appointment)
        .filter(
            Appointment.id == appointment_id,
            Appointment.user_id == user_id,
            Appointment.status == "booked",
        )
        .first()
    )

    if not appointment:
        return None

    appointment.status = "cancelled"

    db.commit()
    db.refresh(appointment)

    return appointment


# ---------------------------------------------------------
# GET USER APPOINTMENTS
# ---------------------------------------------------------


def get_user_appointments(
    db: Session,
    user_id: int,
):
    appointments = (
        db.query(Appointment)
        .filter(
            Appointment.user_id == user_id,
            Appointment.status == "booked",
        )
        .all()
    )

    return appointments


# ---------------------------------------------------------
# FIND NEARBY SLOTS
# ---------------------------------------------------------


def get_nearby_slots(
    db: Session,
    appointment_date: date,
    requested_time: time,
    service_duration: int,
    number_of_slots: int = 3,
):
    available_slots = get_available_slots(
        db=db,
        appointment_date=appointment_date,
        service_duration=service_duration,
    )

    if not available_slots:
        return []

    requested_datetime = datetime.combine(
        appointment_date,
        requested_time,
    )

    available_slots.sort(
        key=lambda slot: abs(
            (
                datetime.combine(appointment_date, slot) - requested_datetime
            ).total_seconds()
        )
    )

    return available_slots[:number_of_slots]
