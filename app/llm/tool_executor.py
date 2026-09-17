import json
from datetime import date, time

from ..tools.appointment_tools import (
    check_availability,
    find_nearby_slots,
    create_booking,
    get_my_appointments,
    get_my_appointment,
    cancel_my_appointment,
    reschedule_my_appointment,
    get_services,
)


def execute_tool(db, user_id, tool_call):
    function_name = tool_call.function.name
    arguments = json.loads(tool_call.function.arguments)

    if function_name == "check_availability":
        return check_availability(
            db=db,
            appointment_date=date.fromisoformat(arguments["appointment_date"]),
            service_name=arguments["service_name"],
        )

    elif function_name == "find_nearby_slots":
        return find_nearby_slots(
            db=db,
            appointment_date=date.fromisoformat(arguments["appointment_date"]),
            requested_time=time.fromisoformat(arguments["requested_time"]),
            service_name=arguments["service_name"],
        )

    elif function_name == "create_booking":
        return create_booking(
            db=db,
            user_id=user_id,
            appointment_date=date.fromisoformat(arguments["appointment_date"]),
            appointment_time=time.fromisoformat(arguments["appointment_time"]),
            service_name=arguments["service_name"],
        )

    elif function_name == "get_my_appointments":
        return get_my_appointments(
            db=db,
            user_id=user_id,
        )
    elif function_name == "get_services":
        return get_services(db=db)

    elif function_name == "get_my_appointment":
        return get_my_appointment(
            db=db,
            user_id=user_id,
            appointment_id=int(arguments["appointment_id"]),
        )

    elif function_name == "cancel_my_appointment":
        return cancel_my_appointment(
            db=db,
            user_id=user_id,
            appointment_id=int(arguments["appointment_id"]),
        )

    elif function_name == "reschedule_my_appointment":
        return reschedule_my_appointment(
            db=db,
            user_id=user_id,
            appointment_id=int(arguments["appointment_id"]),
            new_date=date.fromisoformat(arguments["new_date"]),
            new_time=time.fromisoformat(arguments["new_time"]),
        )

    return {
        "success": False,
        "message": f"Unknown tool: {function_name}",
    }
