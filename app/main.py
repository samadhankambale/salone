from fastapi import FastAPI

from .routers.appointments import router as appointments_router
from .routers.auth import router as auth_router
from .routers.chat import router as chat_router

app = FastAPI(
    title="Salon AI Receptionist",
    description="Backend API for salon appointment management",
    version="1.0.0",
)


app.include_router(auth_router)
app.include_router(appointments_router)
app.include_router(chat_router)


@app.get("/")
def root():
    return {"message": "Salon AI Receptionist API is running"}
