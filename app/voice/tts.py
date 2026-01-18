from gtts import gTTS
import uuid
import os


def text_to_speech(text: str, language: str) -> str:
    lang = "ta" if language == "ta" else "en"
    filename = f"audio_{uuid.uuid4()}.mp3"

    tts = gTTS(text=text, lang=lang)
    tts.save(filename)

    return filename
