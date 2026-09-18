from app.celery_app import celery_app
from app.services.pipeline import run_dubbing_pipeline

@celery_app.task(bind=True)
def process_video_task(self, job_id: str):
    run_dubbing_pipeline(job_id)