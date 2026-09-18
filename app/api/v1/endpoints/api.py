from fastapi import APIRouter
from app.api.v1.endpoints import videos

api_router = APIRouter()
api_router.include_router(videos.router, prefix="/videos", tags=["Videos & Dubbing Pipeline"])