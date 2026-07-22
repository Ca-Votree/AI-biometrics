"""
Student Management API Routes
Quản lý thông tin sinh viên và đăng ký khuôn mặt.
"""
import os
import shutil
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.config import settings
from app.database.session import get_db
from app.database import crud
from app.core.pipeline import recognition_pipeline

router = APIRouter(prefix="/api/students", tags=["students"])


@router.get("/")
async def list_students(
    skip: int = 0,
    limit: int = 100,
    class_name: str = None,
    face_registered: bool = None,
    db: AsyncSession = Depends(get_db),
):
    """Lấy danh sách sinh viên."""
    students = await crud.get_all_students(
        db, skip=skip, limit=limit, 
        class_name=class_name, face_registered=face_registered
    )
    return {
        "students": [
            {
                "student_id": s.student_id,
                "full_name": s.full_name,
                "class_name": s.class_name,
                "department": s.department,
                "face_registered": s.face_registered,
                "num_face_images": s.num_face_images,
            }
            for s in students
        ],
        "total": len(students),
    }


@router.post("/")
async def create_student(
    student_id: str = Form(...),
    full_name: str = Form(...),
    class_name: str = Form(None),
    department: str = Form(None),
    email: str = Form(None),
    phone: str = Form(None),
    db: AsyncSession = Depends(get_db),
):
    """Tạo sinh viên mới."""
    existing = await crud.get_student(db, student_id)
    if existing:
        raise HTTPException(status_code=400, detail=f"Sinh viên {student_id} đã tồn tại")

    student = await crud.create_student(
        db, student_id=student_id, full_name=full_name,
        class_name=class_name, department=department,
        email=email, phone=phone,
    )
    return {"message": f"Đã tạo sinh viên {student_id}", "student_id": student_id}


@router.get("/{student_id}")
async def get_student(student_id: str, db: AsyncSession = Depends(get_db)):
    """Lấy thông tin sinh viên."""
    student = await crud.get_student(db, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Sinh viên không tồn tại")
    
    return {
        "student_id": student.student_id,
        "full_name": student.full_name,
        "class_name": student.class_name,
        "department": student.department,
        "email": student.email,
        "phone": student.phone,
        "face_registered": student.face_registered,
        "num_face_images": student.num_face_images,
        "created_at": student.created_at.isoformat() if student.created_at else None,
    }


@router.post("/{student_id}/register-face")
async def register_face(
    student_id: str,
    files: list[UploadFile] = File(...),
    db: AsyncSession = Depends(get_db),
):
    """
    Đăng ký khuôn mặt cho sinh viên.
    Upload nhiều ảnh khuôn mặt để tăng độ chính xác.
    """
    import cv2
    import numpy as np
    
    # Kiểm tra sinh viên tồn tại
    student = await crud.get_student(db, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Sinh viên không tồn tại")

    # Lưu ảnh và đọc vào numpy array
    face_dir = Path(settings.FACES_DIR) / student_id
    face_dir.mkdir(parents=True, exist_ok=True)
    
    images = []
    for i, file in enumerate(files):
        # Lưu ảnh gốc
        file_path = face_dir / f"face_{i+1}{Path(file.filename).suffix}"
        content = await file.read()
        
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Đọc ảnh bằng OpenCV
        nparr = np.frombuffer(content, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is not None:
            images.append(img)

    if not images:
        raise HTTPException(status_code=400, detail="Không có ảnh hợp lệ nào")

    # Đăng ký qua pipeline
    result = recognition_pipeline.register_face(student_id, images)
    
    if result["success"]:
        await crud.update_student_face_status(
            db, student_id, registered=True, num_images=result["num_images_processed"]
        )
        return result
    else:
        raise HTTPException(status_code=400, detail=result["message"])


@router.get("/stats/overview")
async def student_stats(db: AsyncSession = Depends(get_db)):
    """Thống kê tổng quan sinh viên."""
    total = await crud.get_student_count(db)
    registered = await crud.get_all_students(db, face_registered=True)
    
    return {
        "total_students": total,
        "face_registered": len(registered),
        "face_not_registered": total - len(registered),
    }
