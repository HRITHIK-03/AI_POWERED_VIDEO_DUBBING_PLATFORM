import logging
from huggingface_hub import InferenceClient
from app.config import settings

logger = logging.getLogger("dubbing_platform")

class OpenAITranslationProvider:
    def __init__(self):
        api_key = settings.HUGGINGFACE_API_KEY
        if not api_key:
            raise ValueError("Hugging Face API key is missing. Please set HUGGINGFACE_API_KEY in your .env file.")
        
        self.client = InferenceClient(api_key=api_key)

    def translate(self, text: str, target_language: str) -> str:
        logger.info(f"Translating text to {target_language} using Hugging Face Llama 3.1...")
        response = self.client.chat_completion(
            model="meta-llama/Llama-3.1-8B-Instruct",  # Updated to active router model ID
            messages=[
                {"role": "system", "content": f"Translate the following text accurately into {target_language}. Return only the translated text."},
                {"role": "user", "content": text}
            ],
            max_tokens=500
        )
        return response.choices[0].message.content