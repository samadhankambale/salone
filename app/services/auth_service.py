"""Authentication helpers for the Salon AI Receptionist."""

from sqlalchemy import or_
from sqlalchemy.orm import Session

from ..models import User


def authenticate_user(db: Session, identifier: str, password: str):
    """
    Return a user when their email/name and password match.
    Otherwise, return None.
    """

    normalized_identifier = identifier.strip()

    if not normalized_identifier or not password:
        return None

    return (
        db.query(User)
        .filter(
            or_(
                User.email == normalized_identifier,
                User.name == normalized_identifier,
            ),
            User.password == password,
        )
        .first()
    )


def register_user(
    db: Session,
    name: str,
    email: str,
    password: str,
    phone: str | None = None,
):
    """
    Create a new user.

    Returns:
        User object when registration succeeds.
        None when the email or username already exists.
    """

    name = name.strip()
    email = email.strip().lower()
    password = password.strip()

    if not name or not email or not password:
        return None

    # Check whether email or name already exists.
    existing_user = (
        db.query(User)
        .filter(
            or_(
                User.email == email,
                User.name == name,
            )
        )
        .first()
    )

    if existing_user:
        return None

    new_user = User(
        name=name,
        email=email,
        password=password,
        phone=phone.strip() if phone else None,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user
