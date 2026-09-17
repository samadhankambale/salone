from app.voice.speech_to_text import listen_and_transcribe
from app.voice.text_to_speech import speak


if __name__ == "__main__":
    user_text = listen_and_transcribe()

    print("You said:", user_text)

    speak(f"You said: {user_text}")