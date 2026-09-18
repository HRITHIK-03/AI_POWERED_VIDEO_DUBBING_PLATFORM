from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.config import settings
from app.api.v1.endpoints.api import api_router
from app.database import engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.PROJECT_NAME, version="1.0.0")

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

# Mount static folder for frontend UI
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", include_in_schema=False)
def read_root():
    return FileResponse("static/index.html")

@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "healthy", "service": settings.PROJECT_NAME, "storage": "local"}