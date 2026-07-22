"""
FastAPI Main Application
Entry point cho hệ thống điểm danh AI.
"""
import os
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.config import settings, BASE_DIR
from app.database.session import init_db, close_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup + shutdown events."""
    # === STARTUP ===
    logger.info(f"🚀 Khởi động {settings.APP_NAME}...")
    
    # Tạo các thư mục cần thiết
    dirs_to_create = [
        Path(settings.FACES_DIR),
        Path(settings.FAISS_INDEX_PATH).parent,
        Path(settings.LOG_FILE).parent,
        BASE_DIR / "models",
    ]
    for d in dirs_to_create:
        d.mkdir(parents=True, exist_ok=True)
    
    # Khởi tạo Database
    await init_db()

    logger.info("AI Pipeline sẽ được khởi tạo khi có request đầu tiên (lazy loading)")
    
    logger.info(f"✅ {settings.APP_NAME} API Backend đã sẵn sàng!")
    logger.info(f"📡 API đang chạy tại: http://{settings.HOST}:{settings.PORT}")
    
    yield
    
    # === SHUTDOWN ===
    logger.info("Đang tắt ứng dụng...")
    await close_db()
    logger.info("👋 Đã tắt ứng dụng")


app = FastAPI(
    title=settings.APP_NAME,
    description="Hệ thống điểm danh tự động sử dụng nhận diện khuôn mặt AI",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# === Register API Routes ===
from app.api.routes.students import router as students_router
from app.api.routes.attendance import router as attendance_router
from app.api.routes.camera import router as camera_router

app.include_router(students_router)
app.include_router(attendance_router)
app.include_router(camera_router)

# === Root Config ===
@app.get("/")
async def root():
    return {
        "message": "AI Biometrics API Backend is running. Please start the Frontend separately via Live Server or HTTP Server.",
        "docs": "/docs"
    }



# === Health Check ===
@app.get("/api/health")
async def health_check():
    """API health check."""
    from app.core.pipeline import recognition_pipeline
    from app.core.matcher import face_matcher
    from app.camera.capture import video_capture
    
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "pipeline_ready": recognition_pipeline.is_initialized,
        "faiss_vectors": face_matcher.total_vectors if face_matcher.is_initialized else 0,
        "camera_running": video_capture.is_running,
    }
