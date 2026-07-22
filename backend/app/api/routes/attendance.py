"""
Attendance API Routes
Quản lý phiên điểm danh và kết quả.
"""
import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.database.session import get_db
from app.database import crud

router = APIRouter(prefix="/api/attendance", tags=["attendance"])


class SessionCreate(BaseModel):
    session_name: str
    course_name: str = None
    room: str = None
    instructor: str = None


@router.post("/sessions")
async def create_session(data: SessionCreate, db: AsyncSession = Depends(get_db)):
    """Tạo phiên điểm danh mới."""
    # Kiểm tra có phiên đang active không
    active = await crud.get_active_session(db)
    if active:
        raise HTTPException(
            status_code=400, 
            detail=f"Đang có phiên điểm danh hoạt động: {active.session_name}. "
                   f"Vui lòng kết thúc trước khi tạo phiên mới."
        )
    
    session = await crud.create_session(
        db, 
        session_name=data.session_name,
        course_name=data.course_name,
        room=data.room,
        instructor=data.instructor,
    )
    return {
        "message": f"Đã tạo phiên: {data.session_name}",
        "session_id": session.id,
    }


@router.get("/sessions/active")
async def get_active_session(db: AsyncSession = Depends(get_db)):
    """Lấy phiên điểm danh đang hoạt động."""
    session = await crud.get_active_session(db)
    if not session:
        return {"active": False, "session": None}
    
    count = await crud.get_attendance_count(db, session.id)
    
    return {
        "active": True,
        "session": {
            "id": session.id,
            "session_name": session.session_name,
            "course_name": session.course_name,
            "room": session.room,
            "instructor": session.instructor,
            "start_time": session.start_time.isoformat(),
            "total_recognized": count,
            "total_unknown": session.total_unknown or 0,
        }
    }


@router.post("/sessions/{session_id}/end")
async def end_session(session_id: int, db: AsyncSession = Depends(get_db)):
    """Kết thúc phiên điểm danh."""
    await crud.end_session(db, session_id)
    return {"message": f"Đã kết thúc phiên {session_id}"}


@router.get("/sessions")
async def list_sessions(
    skip: int = 0, limit: int = 50,
    db: AsyncSession = Depends(get_db),
):
    """Lấy danh sách phiên điểm danh."""
    sessions = await crud.get_all_sessions(db, skip=skip, limit=limit)
    return {
        "sessions": [
            {
                "id": s.id,
                "session_name": s.session_name,
                "course_name": s.course_name,
                "room": s.room,
                "start_time": s.start_time.isoformat() if s.start_time else None,
                "end_time": s.end_time.isoformat() if s.end_time else None,
                "is_active": s.is_active,
                "total_recognized": s.total_recognized or 0,
            }
            for s in sessions
        ]
    }


@router.get("/sessions/{session_id}/records")
async def get_records(session_id: int, db: AsyncSession = Depends(get_db)):
    """Lấy danh sách điểm danh của phiên."""
    records = await crud.get_attendance_by_session(db, session_id)
    
    result = []
    for r in records:
        student = await crud.get_student(db, r.student_id)
        result.append({
            "student_id": r.student_id,
            "full_name": student.full_name if student else "N/A",
            "class_name": student.class_name if student else "N/A",
            "check_in_time": r.check_in_time.isoformat(),
            "similarity_score": r.similarity_score,
            "method": r.method,
            "status": r.status,
        })
    
    return {
        "session_id": session_id,
        "records": result,
        "total": len(result),
    }


@router.get("/dashboard")
async def dashboard_stats(db: AsyncSession = Depends(get_db)):
    """Dữ liệu tổng quan cho dashboard."""
    total_students = await crud.get_student_count(db)
    registered_students = await crud.get_all_students(db, face_registered=True)
    active_session = await crud.get_active_session(db)
    all_sessions = await crud.get_all_sessions(db, limit=10)
    
    active_count = 0
    if active_session:
        active_count = await crud.get_attendance_count(db, active_session.id)
    
    return {
        "total_students": total_students,
        "registered_faces": len(registered_students),
        "active_session": {
            "id": active_session.id,
            "name": active_session.session_name,
            "attendance_count": active_count,
        } if active_session else None,
        "recent_sessions": [
            {
                "id": s.id,
                "name": s.session_name,
                "date": s.start_time.isoformat() if s.start_time else None,
                "total": s.total_recognized or 0,
            }
            for s in all_sessions
        ],
    }
