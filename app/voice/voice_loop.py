from ..database import SessionLocal
from ..services.auth_service import authenticate_user
from ..llm.receptionist import chat

from .speech_to_text import listen_and_transcribe
from .text_to_speech import speak


def login_voice(db):
    print("Please sign in to continue.")

    identifier = input("Email or username: ").strip()

    if identifier.lower() in {"exit", "quit", "bye"}:
        return None

    password = input("Password: ")

    user = authenticate_user(db, identifier, password)

    if user is None:
        speak("Incorrect email or username or password.")
        return None

    return user


def start_voice_chat():
    print("=================================")
    print("      Welcome to Salon AI Voice")
    print("=================================")

    db = SessionLocal()

    try:
        current_user = login_voice(db)

        if current_user is None:
            return

        greeting = (
            f"Hi {current_user.name}! "
            "I'm your salon receptionist. How can I help you?"
        )

        print(f"\nBot: {greeting}")
        speak(greeting)

        messages = None

        while True:
            user_message = listen_and_transcribe()

            if not user_message or len(user_message.strip()) < 2:
                print("I could not clearly hear you. Please try again.")
                speak("I could not clearly hear you. Please try again.")
                continue

            print(f"\nYou: {user_message}")

            if user_message.lower().strip() in {"exit", "quit", "bye"}:
                response = "Thank you for contacting us. Goodbye!"

                print(f"\nBot: {response}")
                speak(response)

                break

            try:
                response, messages = chat(
                    db=db,
                    user_id=current_user.id,
                    user_message=user_message,
                    messages=messages,
                )

                print(f"\nBot: {response}")
                speak(response)

            except Exception as e:
                response = (
                    "Sorry, something went wrong while processing "
                    "your request."
                )

                print(f"\nBot: {response}")
                print(f"Error: {e}")

                speak(response)

    finally:
        db.close()


if __name__ == "__main__":
    start_voice_chat()