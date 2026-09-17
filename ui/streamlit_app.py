import sys
import hashlib
from pathlib import Path

import requests
import streamlit as st

# --------------------------------------------------
# PROJECT IMPORT PATH
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# --------------------------------------------------
# IMPORTS
# --------------------------------------------------

from app.database import SessionLocal
from app.services.auth_service import authenticate_user
from app.voice.speech_to_text import transcribe_uploaded_audio


# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

BACKEND_URL = "http://127.0.0.1:8000"


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Salon AI Receptionist",
    page_icon="💇",
    layout="centered",
)


# --------------------------------------------------
# SESSION INITIALIZATION
# --------------------------------------------------

def initialize_session():

    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if "current_user" not in st.session_state:
        st.session_state.current_user = None

    if "messages" not in st.session_state:
        st.session_state.messages = None

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    if "auth_mode" not in st.session_state:
        st.session_state.auth_mode = "login"

    # Used to prevent the same audio recording from
    # being processed repeatedly during Streamlit reruns.
    if "last_audio_hash" not in st.session_state:
        st.session_state.last_audio_hash = None


# --------------------------------------------------
# LOGIN PAGE
# --------------------------------------------------

def login_page():

    st.title("💇 Salon AI Receptionist")

    tab_login, tab_register = st.tabs(["Login", "Register"])

    # --------------------------------------------------
    # LOGIN TAB
    # --------------------------------------------------

    with tab_login:

        st.subheader("Sign in to continue")

        identifier = st.text_input(
            "Email or username",
            placeholder="Enter your email or username",
            key="login_identifier",
        )

        password = st.text_input(
            "Password",
            type="password",
            placeholder="Enter your password",
            key="login_password",
        )

        if st.button("Login", use_container_width=True):

            if not identifier or not password:
                st.warning(
                    "Please enter both your email/username and password."
                )
                return

            db = SessionLocal()

            try:

                user = authenticate_user(
                    db,
                    identifier,
                    password,
                )

                if user is None:
                    st.error("Incorrect email/username or password.")
                    return

                st.session_state.authenticated = True
                st.session_state.current_user = user

                # Reset conversation for new login session
                st.session_state.messages = None
                st.session_state.chat_history = []
                st.session_state.last_audio_hash = None

                st.rerun()

            except Exception as e:

                st.error("Something went wrong while logging in.")
                st.exception(e)

            finally:
                db.close()

    # --------------------------------------------------
    # REGISTER TAB
    # --------------------------------------------------

    with tab_register:

        st.subheader("Create a new account")

        name = st.text_input(
            "Full name",
            placeholder="Enter your name",
            key="register_name",
        )

        email = st.text_input(
            "Email",
            placeholder="Enter your email address",
            key="register_email",
        )

        phone = st.text_input(
            "Phone number",
            placeholder="Optional",
            key="register_phone",
        )

        password = st.text_input(
            "Password",
            type="password",
            placeholder="Create a password",
            key="register_password",
        )

        confirm_password = st.text_input(
            "Confirm password",
            type="password",
            placeholder="Re-enter your password",
            key="register_confirm_password",
        )

        if st.button("Create account", use_container_width=True):

            if not name or not email or not password:
                st.warning("Name, email, and password are required.")
                return

            if password != confirm_password:
                st.error("Passwords do not match.")
                return

            try:

                response = requests.post(
                    f"{BACKEND_URL}/auth/register",
                    json={
                        "name": name,
                        "email": email,
                        "password": password,
                        "phone": phone or None,
                    },
                    timeout=30,
                )

                response.raise_for_status()

                data = response.json()

                if data.get("success"):

                    st.success(
                        "Registration successful! You can now log in."
                    )

                else:

                    st.error(
                        data.get(
                            "message",
                            "Registration failed.",
                        )
                    )

            except requests.exceptions.ConnectionError:

                st.error(
                    "Could not connect to FastAPI. "
                    "Please make sure Uvicorn is running."
                )

            except requests.exceptions.HTTPError as e:

                st.error(
                    f"Registration failed: {e.response.status_code}"
                )

            except Exception as e:

                st.error("Something went wrong during registration.")
                st.exception(e)


# --------------------------------------------------
# LOGOUT
# --------------------------------------------------

def logout():

    st.session_state.authenticated = False
    st.session_state.current_user = None
    st.session_state.messages = None
    st.session_state.chat_history = []
    st.session_state.last_audio_hash = None

    st.rerun()


# --------------------------------------------------
# SEND MESSAGE TO BACKEND
# --------------------------------------------------

def send_message_to_backend(user_message, current_user):

    try:

        response_data = requests.post(
            f"{BACKEND_URL}/chat",
            json={
                "user_id": current_user.id,
                "message": user_message,
                "messages": st.session_state.messages,
            },
            timeout=120,
        )

        response_data.raise_for_status()

        data = response_data.json()

        response = data["response"]
        messages = data["messages"]

        return response, messages, None

    except requests.exceptions.ConnectionError:

        error_message = (
            "I could not connect to the FastAPI backend. "
            "Please make sure Uvicorn is running on port 8000."
        )

        return None, None, error_message

    except requests.exceptions.Timeout:

        error_message = (
            "The request took too long to complete. "
            "Please try again."
        )

        return None, None, error_message

    except requests.exceptions.HTTPError as e:

        error_message = (
            f"FastAPI returned an error: "
            f"{e.response.status_code}"
        )

        return None, None, error_message

    except Exception as e:

        error_message = (
            "Sorry, something went wrong while processing your request."
        )

        return None, None, error_message


# --------------------------------------------------
# DISPLAY ASSISTANT RESPONSE
# --------------------------------------------------

def process_user_message(user_message, current_user):

    # Add user's message to chat history
    st.session_state.chat_history.append(
        {
            "role": "user",
            "content": user_message,
        }
    )

    # Display user's message immediately
    with st.chat_message("user"):
        st.markdown(user_message)

    # Call FastAPI backend
    with st.chat_message("assistant"):

        with st.spinner("Thinking..."):

            response, messages, error_message = send_message_to_backend(
                user_message,
                current_user,
            )

        if error_message:

            st.error(error_message)

            st.session_state.chat_history.append(
                {
                    "role": "assistant",
                    "content": error_message,
                }
            )

            return

        st.markdown(response)

    # Save Groq conversation messages
    st.session_state.messages = messages

    # Save assistant response for future reruns
    st.session_state.chat_history.append(
        {
            "role": "assistant",
            "content": response,
        }
    )


# --------------------------------------------------
# CHAT PAGE
# --------------------------------------------------

def chat_page():

    current_user = st.session_state.current_user

    # --------------------------------------------------
    # SIDEBAR
    # --------------------------------------------------

    with st.sidebar:

        st.title("Salon AI")

        st.write(
            f"Welcome, **{current_user.name}**!"
        )

        st.divider()

        if st.button("Logout", use_container_width=True):
            logout()

    # --------------------------------------------------
    # HEADER
    # --------------------------------------------------

    st.title("💇 Salon AI Receptionist")

    st.write(
        "Ask about services, availability, bookings, "
        "cancellations, or rescheduling."
    )

    st.divider()

    # --------------------------------------------------
    # DISPLAY CHAT HISTORY
    # --------------------------------------------------

    for message in st.session_state.chat_history:

        with st.chat_message(message["role"]):

            st.markdown(message["content"])

    # --------------------------------------------------
    # TEXT CHAT INPUT
    # --------------------------------------------------

    user_message = st.chat_input(
        "Type your message here..."
    )

    if user_message:

        process_user_message(
            user_message,
            current_user,
        )

    # --------------------------------------------------
    # VOICE INPUT
    # --------------------------------------------------

    st.markdown("### 🎙️ Or speak to the receptionist")

    audio_value = st.audio_input(
        "Record your message",
        key="voice_recorder",
    )

    if audio_value is None:
        return

    # Read recorded audio bytes
    audio_bytes = audio_value.getvalue()

    if not audio_bytes:
        return

    # Create a unique hash for this recording
    audio_hash = hashlib.md5(audio_bytes).hexdigest()

    # Prevent duplicate processing when Streamlit reruns
    if audio_hash == st.session_state.last_audio_hash:
        return

    # Store hash immediately
    st.session_state.last_audio_hash = audio_hash

    # Transcribe audio
    with st.spinner("Listening and transcribing..."):

        try:

            user_message = transcribe_uploaded_audio(
                audio_bytes
            )

        except Exception as e:

            st.error("Could not transcribe your recording.")
            st.exception(e)
            return

    # Check transcription result
    if not user_message or not user_message.strip():

        st.warning(
            "I couldn't understand the recording. "
            "Please try speaking again."
        )

        return

    # Display what the user said
    st.info(f"You said: {user_message}")

    # Send transcribed message through existing chatbot
    process_user_message(
        user_message,
        current_user,
    )


# --------------------------------------------------
# MAIN
# --------------------------------------------------

def main():

    initialize_session()

    if not st.session_state.authenticated:

        login_page()

    else:

        chat_page()


# --------------------------------------------------
# RUN APPLICATION
# --------------------------------------------------

if __name__ == "__main__":
    main()