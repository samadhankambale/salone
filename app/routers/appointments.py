from datetime import date
from ..database import SessionLocal
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..schemas import AppointmentCreate
from ..services.appointment_service import (
    get_available_slots,
    book_appointment,
    get_user_appointments,
    cancel_appointment,
)

router = APIRouter(prefix="/appointments", tags=["Appointments"])


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


@router.get("/available")
def available_slots(appointment_date: date, db: Session = Depends(get_db)):
    slots = get_available_slots(db=db, appointment_date=appointment_date)

    return {
        "date": appointment_date,
        "available_slots": [slot.strftime("%H:%M") for slot in slots],
    }


@router.post("/book")
def create_appointment(
    appointment_data: AppointmentCreate, db: Session = Depends(get_db)
):
    appointment = book_appointment(
        db=db,
        user_id=appointment_data.user_id,
        service_id=appointment_data.service_id,
        appointment_date=appointment_data.appointment_date,
        appointment_time=appointment_data.appointment_time,
    )

    # If the service function returns a specific error message,
    # send that message directly to the client.
    if isinstance(appointment, dict):
        return appointment

    # If no appointment was returned, the slot is unavailable.
    if not appointment:
        return {
            "success": False,
            "message": "Sorry, that slot is already booked.",
        }

    # Successful booking.
    return {
        "success": True,
        "message": "Appointment booked successfully!",
        "appointment_id": appointment.id,
        "date": appointment.appointment_date,
        "time": appointment.appointment_time,
    }


@router.get("/user/{user_id}")
def user_appointments(user_id: int, db: Session = Depends(get_db)):
    appointments = get_user_appointments(db=db, user_id=user_id)

    return {
        "user_id": user_id,
        "appointments": [
            {
                "appointment_id": appointment.id,
                "service_id": appointment.service_id,
                "date": appointment.appointment_date,
                "time": appointment.appointment_time,
                "status": appointment.status,
            }
            for appointment in appointments
        ],
    }


@router.post("/{appointment_id}/cancel")
def cancel_user_appointment(
    appointment_id: int, user_id: int, db: Session = Depends(get_db)
):
    appointment = cancel_appointment(
        db=db, appointment_id=appointment_id, user_id=user_id
    )

    if not appointment:
        return {
            "message": "Appointment not found, does not belong to this user, or is already cancelled."
        }

    return {
        "message": "Appointment cancelled successfully!",
        "appointment_id": appointment.id,
        "status": appointment.status,
    }
