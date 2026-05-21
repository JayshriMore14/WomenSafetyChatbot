"""Voice input and text-to-speech helpers."""

from __future__ import annotations


def speech_to_text(timeout: int = 5) -> tuple[str, str | None]:
    """Capture microphone audio and convert it to text.

    SpeechRecognition may need PyAudio installed on the user's machine. The app
    catches errors and displays friendly instructions if microphone support is
    unavailable.
    """
    try:
        import speech_recognition as sr
    except Exception as error:
        return "", f"SpeechRecognition is not available: {error}"

    recognizer = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = recognizer.listen(source, timeout=timeout)
        return recognizer.recognize_google(audio), None
    except Exception as error:
        return "", f"Could not capture voice input: {error}"


def speak_text(text: str) -> str:
    """Read response text aloud using pyttsx3."""
    try:
        import pyttsx3

        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()
        return "Voice response played."
    except Exception as error:
        return f"Text-to-speech unavailable: {error}"
