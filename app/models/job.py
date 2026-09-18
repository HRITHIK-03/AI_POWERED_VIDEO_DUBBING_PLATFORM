from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Text
from app.database import Base

class JobStatus:
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"

class JobModel(Base):
    __tablename__ = "dubbing_jobs"

    id = Column(String, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    target_language = Column(String, nullable=False)
    status = Column(String, default=JobStatus.PENDING, nullable=False)
    progress = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    output_video_path = Column(String, nullable=True)
    transcript_path = Column(String, nullable=True)
    subtitle_path = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)