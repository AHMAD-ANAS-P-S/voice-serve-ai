from faster_whisper import WhisperModel
import os
import re


class LanguageVoiceAgent:
    def __init__(self):
        # Small model is enough for hackathon + CPU
        self.model = WhisperModel(
            "small",
            device="cpu",
            compute_type="int8"
        )

    def speech_to_text(self, audio_path: str) -> dict:
        """
        Converts speech to text and decides language.

        RULE:
        - If Tamil Unicode characters are present → Tamil
        - Otherwise → English
        """

        if not os.path.exists(audio_path):
            raise FileNotFoundError("Audio file not found")

        # Step 1: Transcribe audio
        try:
            segments, _ = self.model.transcribe(
                audio_path,
                task="transcribe"
            )
        except Exception as e:
            print(f"Whisper Error: {e}")
            return {"text": "", "language": "en"}

        # Step 2: Build full text
        text_parts = []
        for segment in segments:
            text_parts.append(segment.text.strip())

        text = " ".join(text_parts).strip()

        # Step 3: Strict language decision
        # Tamil Unicode block: U+0B80 – U+0BFF
        tamil_pattern = re.compile(r"[\u0B80-\u0BFF]")

        if tamil_pattern.search(text):
            language = "ta"
        else:
            language = "en"

        return {
            "text": text,
            "language": language
        }
