import os
import logging
from groq import Groq
from app.config import settings

logger = logging.getLogger("dubbing_platform")

class OpenAISTTProvider:
    def __init__(self):
        api_key = settings.GROQ_API_KEY or os.getenv("GROQ_API_KEY")
        self.client = Groq(api_key=api_key)

    def transcribe(self, audio_path: str) -> dict:
        logger.info("Transcribing audio using Groq Whisper model...")
        with open(audio_path, "rb") as file:
            transcription = self.client.audio.transcriptions.create(
                file=(audio_path, file.read()),
                model="whisper-large-v3-turbo",
                response_format="verbose_json"
            )
        return transcription.model_dump()