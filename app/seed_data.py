from .database import SessionLocal
from .models import Service


def seed_services():
    db = SessionLocal()

    services = [
        Service(
            name="Haircut", description="Basic haircut", duration_minutes=30, price=300
        ),
        Service(
            name="Beard Trim",
            description="Beard trimming and grooming",
            duration_minutes=20,
            price=200,
        ),
        Service(
            name="Facial",
            description="Basic facial treatment",
            duration_minutes=60,
            price=800,
        ),
        Service(
            name="Hair Spa",
            description="Hair spa and conditioning treatment",
            duration_minutes=60,
            price=1000,
        ),
    ]

    db.add_all(services)
    db.commit()

    db.close()

    print("Services added successfully!")


if __name__ == "__main__":
    seed_services()
