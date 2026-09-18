import os
import subprocess
import logging
from gtts import gTTS
from app.config import settings

logger = logging.getLogger("dubbing_platform")

class TTSProvider:
    def __init__(self, provider_type: str = "gtts"):
        self.provider_type = provider_type

    def synthesize(self, text: str, output_path: str, target_language: str = "English", duration: float = 5.0) -> str:
        if not output_path.endswith(".mp3"):
            output_path = output_path.rsplit(".", 1)[0] + ".mp3"

        logger.info(f"Synthesizing speech. Target Language: '{target_language}', Duration: {duration}s")
        return self._generate_speech(text, output_path, target_language, duration)

    def _generate_speech(self, text: str, output_path: str, target_language: str, duration: float) -> str:
        dir_name = os.path.dirname(output_path)
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)
        
        lang_map = {
            "spanish": "es", "español": "es", "es": "es",
            "french": "fr", "français": "fr", "fr": "fr",
            "german": "de", "deutsch": "de", "de": "de",
            "italian": "it", "italiano": "it", "it": "it",
            "portuguese": "pt", "pt": "pt",
            "english": "en", "en": "en",
            "hindi": "hi", "hi": "hi"
        }
        
        normalized_lang = str(target_language).strip().lower()
        lang_code = lang_map.get(normalized_lang, "en")

        speech_text = text if text and len(text.strip()) > 0 else "Hello world."
        
        # Generate speech audio directly using gTTS
        tts = gTTS(text=speech_text, lang=lang_code, slow=False)
        tts.save(output_path)

        logger.info(f"gTTS speech successfully generated in '{lang_code}' at: {output_path}")
        return output_path