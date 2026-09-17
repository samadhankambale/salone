from .database import SessionLocal
from .models import Appointment
from datetime import date, time


def create_appointment():
    db = SessionLocal()

    appointment = Appointment(
        user_id=1,
        service_id=1,
        appointment_date=date(2026, 9, 10),
        appointment_time=time(14, 0),
        status="booked",
    )

    db.add(appointment)
    db.commit()
    db.refresh(appointment)

    print(f"Appointment created with ID: {appointment.id}")

    db.close()


if __name__ == "__main__":
    create_appointment()
