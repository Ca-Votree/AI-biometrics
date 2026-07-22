"""
AI Biometrics Attendance System - Configuration
"""
import os
from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import Field

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # App
    APP_NAME: str = "AI Biometrics Attendance System"
    APP_ENV: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str = "change-this-to-a-random-secret-key"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Database
    DATABASE_URL: str = f"sqlite+aiosqlite:///{BASE_DIR / 'data' / 'attendance.db'}"

    # AI Model
    DETECTION_MODEL: str = "buffalo_s"
    FACE_DETECTION_THRESHOLD: float = 0.5
    FACE_RECOGNITION_THRESHOLD: float = 0.45
    MAX_FACES_PER_FRAME: int = 50

    # Camera
    CAMERA_SOURCE: str = "0"
    FRAME_WIDTH: int = 640
    FRAME_HEIGHT: int = 480
    FPS: int = 15

    # GPU Configuration
    USE_GPU: bool = True
    GPU_DEVICE: int = 0

    # FAISS
    FAISS_INDEX_PATH: str = str(BASE_DIR / "data" / "faiss_index" / "face_index.bin")
    FAISS_ID_MAP_PATH: str = str(BASE_DIR / "data" / "faiss_index" / "id_map.json")

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = str(BASE_DIR / "data" / "logs" / "app.log")

    # Paths
    FACES_DIR: str = str(BASE_DIR / "data" / "faces")
    MODELS_DIR: str = str(BASE_DIR / "models")

    @property
    def camera_source_parsed(self):
        """Parse camera source - integer for local cam, string for RTSP/URL."""
        try:
            return int(self.CAMERA_SOURCE)
        except ValueError:
            return self.CAMERA_SOURCE

    model_config = {
        "env_file": str(BASE_DIR / ".env"),
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


# Singleton settings instance
settings = Settings()
