import os
import threading

import numpy as np

from faster_whisper import WhisperModel


# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

SAMPLE_RATE = 16000

MICROPHONE_DEVICE = 1


# --------------------------------------------------
# LOAD WHISPER MODEL
# --------------------------------------------------

print("Loading Whisper model...")

model = WhisperModel(
    "small.en",
    device="cpu",
    compute_type="int8",
)

print("Whisper model loaded successfully.")


# --------------------------------------------------
# RECORD AUDIO UNTIL ENTER
# --------------------------------------------------

def record_until_enter(
    filename="user_audio.wav",
    sample_rate=SAMPLE_RATE,
    device=MICROPHONE_DEVICE,
):
    # Local-machine terminal testing only; imported lazily so servers
    # without a microphone/sounddevice can still import this module.
    import sounddevice as sd
    from scipy.io.wavfile import write

    print("\nPress ENTER to start recording.")

    input()

    print("Recording... Press ENTER again to stop.")

    audio_chunks = []
    recording = True

    def callback(indata, frames, time, status):

        if status:
            print(status)

        if recording:
            audio_chunks.append(
                indata.copy()
            )

    with sd.InputStream(
        device=device,
        samplerate=sample_rate,
        channels=1,
        dtype="int16",
        callback=callback,
    ):

        input()

    recording = False

    if not audio_chunks:
        print("No audio recorded.")
        return None

    audio_data = np.concatenate(
        audio_chunks,
        axis=0,
    )

    write(
        filename,
        sample_rate,
        audio_data,
    )

    print(f"Audio saved to {filename}")

    return filename


# --------------------------------------------------
# TRANSCRIBE AUDIO FILE
# --------------------------------------------------

def transcribe_audio(filename="user_audio.wav"):

    print("Transcribing...")

    segments, info = model.transcribe(
        filename,
        language="en",
        task="transcribe",
        vad_filter=True,
        beam_size=5,
        temperature=0,
        condition_on_previous_text=False,
    )

    text = " ".join(
        segment.text.strip()
        for segment in segments
    )

    return text.strip()


# --------------------------------------------------
# TRANSCRIBE STREAMLIT UPLOADED AUDIO
# --------------------------------------------------

def transcribe_uploaded_audio(
    audio_bytes,
    filename="streamlit_audio.wav",
):

    if not audio_bytes:
        return ""

    with open(filename, "wb") as audio_file:

        audio_file.write(audio_bytes)

    return transcribe_audio(filename)


# --------------------------------------------------
# TERMINAL VOICE ASSISTANT FUNCTION
# --------------------------------------------------

def listen_and_transcribe():

    filename = record_until_enter()

    if not filename:
        return ""

    text = transcribe_audio(filename)

    return text


# --------------------------------------------------
# TEST TERMINAL MODE
# --------------------------------------------------

if __name__ == "__main__":

    print("Voice transcription test started.")

    while True:

        text = listen_and_transcribe()

        if not text:
            print("No speech detected.")
            continue

        print(f"You said: {text}")

        if text.lower() in ["exit", "quit", "bye"]:
            break