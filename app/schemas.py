from datetime import date, time

from pydantic import BaseModel


class AppointmentCreate(BaseModel):
    user_id: int
    service_id: int
    appointment_date: date
    appointment_time: time
