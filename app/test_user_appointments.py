from .database import SessionLocal
from .services.appointment_service import get_user_appointments

db = SessionLocal()

appointments = get_user_appointments(db=db, user_id=1)

if appointments:
    print("Your appointments:")

    for appointment in appointments:
        print(
            f"Appointment ID: {appointment.id}, "
            f"Date: {appointment.appointment_date}, "
            f"Time: {appointment.appointment_time}, "
            f"Status: {appointment.status}"
        )
else:
    print("You have no active appointments.")

db.close()
