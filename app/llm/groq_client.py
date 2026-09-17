import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError("GROQ_API_KEY is not set in the .env file")

client = Groq(api_key=api_key)


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "check_availability",
            "description": "Check available appointment slots for a salon service on a specific date.",
            "parameters": {
                "type": "object",
                "properties": {
                    "appointment_date": {
                        "type": "string",
                        "description": "Appointment date in YYYY-MM-DD format.",
                    },
                    "service_name": {
                        "type": "string",
                        "description": "Salon service name, such as Haircut, Beard Trim, Facial, or Hair Spa.",
                    },
                },
                "required": ["appointment_date", "service_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "find_nearby_slots",
            "description": "Find available appointment slots near a requested time.",
            "parameters": {
                "type": "object",
                "properties": {
                    "appointment_date": {
                        "type": "string",
                        "description": "Appointment date in YYYY-MM-DD format.",
                    },
                    "requested_time": {
                        "type": "string",
                        "description": "Requested time in HH:MM 24-hour format.",
                    },
                    "service_name": {
                        "type": "string",
                        "description": "Salon service name.",
                    },
                },
                "required": ["appointment_date", "requested_time", "service_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_booking",
            "description": "Book an appointment for the currently logged-in user.",
            "parameters": {
                "type": "object",
                "properties": {
                    "appointment_date": {
                        "type": "string",
                        "description": "Appointment date in YYYY-MM-DD format.",
                    },
                    "appointment_time": {
                        "type": "string",
                        "description": "Appointment time in HH:MM 24-hour format.",
                    },
                    "service_name": {
                        "type": "string",
                        "description": "Salon service name.",
                    },
                },
                "required": ["appointment_date", "appointment_time", "service_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_my_appointments",
            "description": "Get the currently logged-in user's active appointments.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "cancel_my_appointment",
            "description": "Cancel one of the currently logged-in user's appointments.",
            "parameters": {
                "type": "object",
                "properties": {
                    "appointment_id": {
                        "type": "integer",
                        "description": "ID of the appointment to cancel.",
                    }
                },
                "required": ["appointment_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_my_appointment",
            "description": (
                "Get one booked appointment belonging to the current user "
                "using the appointment ID."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "appointment_id": {
                        "type": "integer",
                        "description": "The appointment ID to look up.",
                    },
                },
                "required": ["appointment_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "reschedule_my_appointment",
            "description": (
                "Reschedule an existing booked appointment to a new date and time. "
                "The appointment ID must belong to the currently logged-in user."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "appointment_id": {
                        "type": "integer",
                        "description": "The ID of the existing appointment.",
                    },
                    "new_date": {
                        "type": "string",
                        "description": "The new appointment date in YYYY-MM-DD format.",
                    },
                    "new_time": {
                        "type": "string",
                        "description": "The new appointment time in HH:MM format.",
                    },
                },
                "required": ["appointment_id", "new_date", "new_time"],
            },
        },
    },
    {
    "type": "function",
    "function": {
        "name": "get_services",
        "description": (
            "Get all active salon services, including their prices "
            "and durations. Use this when the user asks about salon "
            "services, available treatments, prices, or duration."
        ),
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
},
]
