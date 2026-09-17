from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..database import SessionLocal
from ..llm.receptionist import chat

router = APIRouter(prefix="/chat", tags=["Chat"])


class ChatRequest(BaseModel):
    user_id: int
    message: str
    messages: list[dict[str, Any]] | None = None


class ChatResponse(BaseModel):
    response: str
    messages: list[dict[str, Any]]


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


@router.post("")
def chat_message(
    request: ChatRequest,
    db: Session = Depends(get_db),
):
    response, messages = chat(
        db=db,
        user_id=request.user_id,
        user_message=request.message,
        messages=request.messages,
    )

    return {
        "response": response,
        "messages": messages,
    }
