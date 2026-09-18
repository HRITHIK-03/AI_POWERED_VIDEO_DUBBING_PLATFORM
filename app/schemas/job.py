from pydantic import BaseModel

class JobCreateResponse(BaseModel):
    job_id: str
    status: str
    message: str

class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    progress: int
    error_message: str | None = None
    output_video_url: str | None = None
    transcript_url: str | None = None
    subtitle_url: str | None = None