# import uuid
# import os
# from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, status
# from fastapi.responses import FileResponse
# from sqlalchemy.orm import Session
# from app.database import get_db
# from app.models.job import JobModel, JobStatus
# from app.schemas.job import JobCreateResponse, JobStatusResponse
# from app.services.storage import storage_service
# from app.workers.tasks import process_video_task
# from app.config import settings

# router = APIRouter()

# @router.post("/upload", response_model=JobCreateResponse, status_code=status.HTTP_201_CREATED)
# async def upload_video(
#     file: UploadFile = File(...),
#     target_language: str = Form(...),
#     db: Session = Depends(get_db)
# ):
#     ext = f".{file.filename.split('.')[-1].lower()}"
#     if ext not in settings.ALLOWED_EXTENSIONS:
#         raise HTTPException(status_code=400, detail=f"Unsupported format. Allowed: {settings.ALLOWED_EXTENSIONS}")

#     job_id = str(uuid.uuid4())
#     storage_service.save_upload(file.file, job_id)

#     job = JobModel(
#         id=job_id,
#         filename=file.filename,
#         target_language=target_language,
#         status=JobStatus.PENDING,
#         progress=0
#     )
#     db.add(job)
#     db.commit()

#     process_video_task.delay(job_id)

#     return JobCreateResponse(job_id=job_id, status=JobStatus.PENDING, message="Video uploaded and queued successfully.")

# @router.get("/status/{job_id}", response_model=JobStatusResponse)
# def get_job_status(job_id: str, db: Session = Depends(get_db)):
#     job = db.query(JobModel).filter(JobModel.id == job_id).first()
#     if not job:
#         raise HTTPException(status_code=404, detail="Job not found")

#     base_url = "/api/v1/videos/download"
#     return JobStatusResponse(
#         job_id=job.id,
#         status=job.status,
#         progress=job.progress,
#         error_message=job.error_message,
#         output_video_url=f"{base_url}/{job.id}/video" if job.output_video_path else None,
#         transcript_url=f"{base_url}/{job.id}/transcript" if job.transcript_path else None,
#         subtitle_url=f"{base_url}/{job.id}/subtitle" if job.subtitle_path else None
#     )

# @router.get("/download/{job_id}/{file_type}")
# def download_output_file(job_id: str, file_type: str, db: Session = Depends(get_db)):
#     job = db.query(JobModel).filter(JobModel.id == job_id).first()
#     if not job:
#         raise HTTPException(status_code=404, detail="Job not found")
    
#     path_map = {
#         "video": job.output_video_path,
#         "transcript": job.transcript_path,
#         "subtitle": job.subtitle_path
#     }
    
#     file_path = path_map.get(file_type)
#     if not file_path or not os.path.exists(file_path):
#         raise HTTPException(status_code=404, detail="File not ready or found")
        
#     return FileResponse(file_path, filename=os.path.basename(file_path))

# @router.post("/retry/{job_id}")
# def retry_job(job_id: str, db: Session = Depends(get_db)):
#     job = db.query(JobModel).filter(JobModel.id == job_id).first()
#     if not job:
#         raise HTTPException(status_code=404, detail="Job not found")
    
#     job.status = JobStatus.PENDING
#     job.error_message = None
#     job.progress = 0
#     db.commit()

#     process_video_task.delay(job_id)
#     return {"message": "Job re-queued successfully", "job_id": job_id}

import uuid
import os
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, status, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.job import JobModel, JobStatus
from app.schemas.job import JobCreateResponse, JobStatusResponse
from app.services.storage import storage_service
from app.services.pipeline import run_dubbing_pipeline
from app.config import settings

router = APIRouter()

@router.post("/upload", response_model=JobCreateResponse, status_code=status.HTTP_201_CREATED)
async def upload_video(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    target_language: str = Form(...),
    db: Session = Depends(get_db)
):
    ext = f".{file.filename.split('.')[-1].lower()}"
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Unsupported format. Allowed: {settings.ALLOWED_EXTENSIONS}")

    job_id = str(uuid.uuid4())
    storage_service.save_upload(file.file, job_id)

    job = JobModel(
        id=job_id,
        filename=file.filename,
        target_language=target_language,
        status=JobStatus.PENDING,
        progress=0
    )
    db.add(job)
    db.commit()

    # Run pipeline in background thread natively without Celery/Redis
    background_tasks.add_task(run_dubbing_pipeline, job_id)

    return JobCreateResponse(job_id=job_id, status=JobStatus.PENDING, message="Video uploaded and processing started in background.")

@router.get("/status/{job_id}", response_model=JobStatusResponse)
def get_job_status(job_id: str, db: Session = Depends(get_db)):
    job = db.query(JobModel).filter(JobModel.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    base_url = "/api/v1/videos/download"
    return JobStatusResponse(
        job_id=job.id,
        status=job.status,
        progress=job.progress,
        error_message=job.error_message,
        output_video_url=f"{base_url}/{job.id}/video" if job.output_video_path else None,
        transcript_url=f"{base_url}/{job.id}/transcript" if job.transcript_path else None,
        subtitle_url=f"{base_url}/{job.id}/subtitle" if job.subtitle_path else None
    )

@router.get("/download/{job_id}/{file_type}")
def download_output_file(job_id: str, file_type: str, db: Session = Depends(get_db)):
    job = db.query(JobModel).filter(JobModel.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    path_map = {
        "video": job.output_video_path,
        "transcript": job.transcript_path,
        "subtitle": job.subtitle_path
    }
    
    file_path = path_map.get(file_type)
    if not file_path or not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not ready or found")
        
    return FileResponse(file_path, filename=os.path.basename(file_path))

@router.post("/retry/{job_id}")
def retry_job(job_id: str, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    job = db.query(JobModel).filter(JobModel.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job.status = JobStatus.PENDING
    job.error_message = None
    job.progress = 0
    db.commit()

    background_tasks.add_task(run_dubbing_pipeline, job_id)
    return {"message": "Job re-queued successfully", "job_id": job_id}