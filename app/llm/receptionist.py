import json
from datetime import datetime

from app.llm.groq_client import client, TOOLS
from app.llm.tool_executor import execute_tool

SYSTEM_PROMPT = """
You are a helpful AI receptionist for a salon.

You can help users:

- check available slots
- find nearby available slots
- book appointments
- view their appointments
- cancel their appointments
- reschedule appointments

Use tools whenever real salon data is required.

Never invent availability, appointments, booking IDs, or cancellation results.

The current logged-in user is already known to the system.
Do not ask the user for their user ID.

BOOKING RULES:

1. When a user wants to book an appointment, first make sure you know:

   - service
   - date
   - time

2. Before booking, check whether the requested slot is available.

3. If the requested slot is available, DO NOT immediately call create_booking.

4. Instead, tell the user that the slot is available and ask:

   "Would you like me to confirm the booking?"

5. Only call create_booking after the user clearly confirms.

6. Confirmation examples include:

   - yes
   - yes please
   - confirm
   - book it
   - go ahead
   - that's fine

7. If the user says no, don't book anything.

8. If the requested slot is unavailable, use find_nearby_slots to suggest alternatives.

9. If the user chooses one of the suggested alternatives, ask for confirmation before booking.

10. Never claim an appointment was booked unless create_booking succeeds.

11. Remember information from the conversation.

12. Do not ask the user to repeat information that is already available.

DATE AND TIME RULES:

13. The current date and time are provided separately below.
    Always use that value when interpreting relative dates.

14. Never guess the current date.

15. Convert natural-language dates into YYYY-MM-DD before calling tools.

16. Convert natural-language times into HH:MM using the 24-hour format.

17. When the user mentions a weekday, calculate the actual calendar date carefully.

18. Always verify that the calculated date matches the requested weekday.

19. If the user says "Sunday", interpret it as the upcoming Sunday.

20. If the user says "next Sunday", interpret it as the Sunday after the upcoming Sunday.

21. If the user says "tomorrow", use exactly one calendar day after today.

22. If the user says "today", use today's date.

23. If the user says "yesterday", do not allow booking because it is in the past.

24. If a weekday and date conflict with each other, do not silently choose one.
    Ask the user to clarify.

25. Before calling a booking tool, internally verify:

    - the date is correct
    - the weekday matches the date
    - the date is not in the past
    - the requested time is valid

26. If the date is ambiguous, ask the user for clarification instead of guessing.

RESCHEDULING RULES:

27. If a user wants to reschedule or change an appointment:

    - Ask for the appointment ID if it is not provided.
    - Use get_my_appointment to retrieve the existing appointment.
    - Ask for the new date and time if they are missing.
    - Check whether the new slot is available before making any changes.
    - Never cancel the existing appointment before confirming that the new slot
      is available.

28. Before rescheduling, tell the user the existing appointment details and
    the proposed new date and time.

29. Ask for confirmation before making any changes.

30. Only make changes after the user clearly confirms.

31. Never claim an appointment was rescheduled unless the database operation
    succeeds.
"""


def serialize_message(message):
    """
    Convert a Groq SDK message object into a normal dictionary.

    This prevents unsupported fields such as annotations from being
    sent back to Groq on the next conversation request.
    """

    if isinstance(message, dict):
        data = message.copy()

    elif hasattr(message, "model_dump"):
        data = message.model_dump(exclude_none=True)

    elif hasattr(message, "dict"):
        data = message.dict(exclude_none=True)

    else:
        data = {
            "role": getattr(message, "role", None),
            "content": getattr(message, "content", None),
        }

    # Remove metadata that Groq does not accept in future requests.
    data.pop("annotations", None)

    return data


def chat(db, user_id, user_message, messages=None):
    """
    Process one user message using Groq and salon tools.

    Returns:
        assistant_response: Text response for the user.
        messages: JSON-serializable conversation history.
    """

    current_datetime = datetime.now()
    current_date = current_datetime.date()
    current_weekday = current_datetime.strftime("%A")

    system_prompt = f"""
{SYSTEM_PROMPT}

CURRENT DATE AND TIME:

Date: {current_date.strftime("%Y-%m-%d")}
Weekday: {current_weekday}
Time: {current_datetime.strftime("%H:%M")}

IMPORTANT:
Use this exact date as today's date.
Do not assume or invent another date.
"""

    # Create a new conversation if this is the first message.
    if messages is None:
        messages = [
            {
                "role": "system",
                "content": system_prompt,
            }
        ]

    # Add the latest user message.
    messages.append(
        {
            "role": "user",
            "content": user_message,
        }
    )

    while True:

        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
        )

        assistant_message = response.choices[0].message

        # Keep the original Groq object for accessing tool calls.
        # Store only a cleaned dictionary in conversation history.
        assistant_message_data = serialize_message(assistant_message)

        messages.append(assistant_message_data)

        # If there are no tool calls, return the normal assistant response.
        if not assistant_message.tool_calls:
            return (
                assistant_message.content or "",
                messages,
            )

        # Execute every tool requested by Groq.
        for tool_call in assistant_message.tool_calls:

            result = execute_tool(
                db=db,
                user_id=user_id,
                tool_call=tool_call,
            )

            # Add the tool result to the conversation.
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(result, default=str),
                }
            )

        # The loop continues so Groq can read the tool result and
        # generate a final natural-language response.
