from .database import SessionLocal
from .models import User


def create_user():
    db = SessionLocal()

    user = User(
        name="Rahul", email="rahul@gmail.com", password="test123", phone="9876543210"
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    print(f"User created with ID: {user.id}")

    db.close()


if __name__ == "__main__":
    create_user()
