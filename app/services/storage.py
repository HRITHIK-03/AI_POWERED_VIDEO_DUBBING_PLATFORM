import os
import shutil
from app.config import settings

class LocalStorageService:
    def __init__(self):
        self.upload_dir = settings.LOCAL_UPLOAD_DIR
        self.output_dir = settings.LOCAL_OUTPUT_DIR
        os.makedirs(self.upload_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)

    def save_upload(self, file_obj, job_id: str) -> str:
        job_folder = os.path.join(self.upload_dir, job_id)
        os.makedirs(job_folder, exist_ok=True)
        file_path = os.path.join(job_folder, "input.mp4")
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file_obj, buffer)
        return file_path

    def get_upload_path(self, job_id: str) -> str:
        return os.path.join(self.upload_dir, job_id, "input.mp4")

    def create_output_dir(self, job_id: str) -> str:
        job_folder = os.path.join(self.output_dir, job_id)
        os.makedirs(job_folder, exist_ok=True)
        return job_folder

storage_service = LocalStorageService()