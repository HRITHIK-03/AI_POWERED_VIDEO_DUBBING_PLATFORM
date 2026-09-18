from abc import ABC, abstractmethod

class BaseSTTProvider(ABC):
    @abstractmethod
    def transcribe(self, audio_path: str) -> dict:
        pass

class BaseTranslationProvider(ABC):
    @abstractmethod
    def translate(self, text: str, target_language: str) -> str:
        pass

class BaseTTSProvider(ABC):
    @abstractmethod
    def synthesize(self, text: str, voice_id: str, output_path: str):
        pass