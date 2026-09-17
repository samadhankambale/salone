from fastapi import APIRouter, Depends
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from ..database import SessionLocal
from ..services.auth_service import register_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    phone: str | None = None


@router.post("/register")
def register(request: RegisterRequest, db: Session = Depends(get_db)):

    user = register_user(
        db=db,
        name=request.name,
        email=request.email,
        password=request.password,
        phone=request.phone,
    )

    if user is None:
        return {
            "success": False,
            "message": "Email or username already exists.",
        }

    return {
        "success": True,
        "message": "Registration successful!",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
        },
    }
