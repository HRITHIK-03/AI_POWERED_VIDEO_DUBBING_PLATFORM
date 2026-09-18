from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Video Dubbing Platform"
    API_V1_STR: str = "/api/v1"
    
    DATABASE_URL: str = "sqlite:///./dubbing.db"
    REDIS_URL: str = "redis://redis:6379/0"
    
    STORAGE_TYPE: str = "local"
    LOCAL_UPLOAD_DIR: str = "./storage/uploads"
    LOCAL_OUTPUT_DIR: str = "./storage/outputs"
    
    MAX_UPLOAD_SIZE_MB: int = 500
    MAX_VIDEO_DURATION_SEC: int = 600
    ALLOWED_EXTENSIONS: list = [".mp4", ".mov", ".avi", ".mkv"]
    
    GROQ_API_KEY: str = ""
    HUGGINGFACE_API_KEY: str = ""  # <--- Added here

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"

settings = Settings()