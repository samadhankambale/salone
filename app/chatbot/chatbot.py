from ..database import SessionLocal
from ..services.auth_service import authenticate_user
from ..llm.receptionist import chat


def login(db):
    """Authenticate one user for this command-line chat session."""

    print("Please sign in to continue.")

    identifier = input("Email or username: ").strip()

    if identifier.lower() in {"exit", "quit", "bye"}:
        return None

    password = input("Password: ")

    user = authenticate_user(db, identifier, password)

    if user is None:
        print("Bot: Incorrect email/username or password.")
        return None

    return user


def start_chat():
    print("=================================")
    print("        Welcome to Salon AI")
    print("=================================")

    db = SessionLocal()

    try:
        # -------------------------
        # LOGIN
        # -------------------------
        current_user = login(db)

        if current_user is None:
            return

        print(f"\nHi {current_user.name}! " "I'm your salon receptionist.")
        print("Type 'exit' anytime to leave.")

        # -------------------------
        # CONVERSATION MEMORY
        # -------------------------
        messages = None

        # -------------------------
        # CHAT LOOP
        # -------------------------
        while True:

            user_message = input("\nYou: ").strip()

            if not user_message:
                continue

            if user_message.lower() in {"exit", "quit", "bye"}:
                print("Bot: Thank you for contacting us. Goodbye!")
                break

            try:
                response, messages = chat(
                    db=db,
                    user_id=current_user.id,
                    user_message=user_message,
                    messages=messages,
                )

                print(f"\nBot: {response}")

            except Exception as e:
                print(
                    "\nBot: Sorry, something went wrong "
                    "while processing your request."
                )
                print(f"Error: {e}")

    finally:
        db.close()


if __name__ == "__main__":
    start_chat()
