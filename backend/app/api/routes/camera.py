"""
Camera Control & WebSocket Streaming
API cho điều khiển camera và streaming video real-time.
"""
import asyncio
import json
import time

import cv2
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.camera.capture import video_capture, frame_processor
from app.core.pipeline import recognition_pipeline
from app.database.session import get_db, async_session_factory
from app.database import crud

router = APIRouter(prefix="/api/camera", tags=["camera"])


@router.post("/start")
async def start_camera():
    """Bắt đầu capture camera."""
    if video_capture.is_running:
        return {"status": "already_running", "message": "Camera đang chạy"}
    
    success = video_capture.start()
    if success:
        return {"status": "started", "message": "Camera đã bắt đầu"}
    else:
        return {"status": "error", "message": "Không thể mở camera"}


@router.post("/stop")
async def stop_camera():
    """Dừng camera."""
    video_capture.stop()
    return {"status": "stopped", "message": "Camera đã dừng"}


@router.get("/status")
async def camera_status():
    """Kiểm tra trạng thái camera."""
    return {
        "running": video_capture.is_running,
        "fps": round(video_capture.fps, 1),
        "frame_count": video_capture.frame_count,
    }


@router.websocket("/ws/stream")
async def video_stream(websocket: WebSocket):
    """
    WebSocket endpoint cho live video streaming + recognition + liveness.
    """
    await websocket.accept()
    logger.info("WebSocket client đã kết nối")



    # Luồng xử lý AI background
    try:
        from fastapi.concurrency import run_in_threadpool
        
        # Cache đơn giản cho thông tin sinh viên để tránh query DB quá nhiều
        student_cache = {}

        async def get_student_info(db, student_id):
            if student_id in student_cache:
                return student_cache[student_id]
            student = await crud.get_student(db, student_id)
            if student:
                student_cache[student_id] = student.full_name
                return student.full_name
            return "Unknown"

        async def process_and_send_result(process_frame):
            try:
                # Xử lý recognition (không vẽ đè để gửi kết quả sạch bên dưới, nhưng có thể lấy data)
                result = await run_in_threadpool(recognition_pipeline.process_frame, process_frame, annotate=False)
                
                if result:
                    # Logic ghi nhận điểm danh & lấy thông tin thêm
                    faces_data = []
                    async with async_session_factory() as db:
                        active_session = await crud.get_active_session(db)
                        
                        for face in result.faces:
                            full_name = "Unknown"
                            if face.identified:
                                full_name = await get_student_info(db, face.student_id)
                                
                                # Ghi nhận điểm danh nếu session đang mở
                                if active_session:
                                    await crud.record_attendance(
                                        db,
                                        session_id=active_session.id,
                                        student_id=face.student_id,
                                        similarity_score=face.similarity,
                                        confidence=face.det_score,
                                    )
                            
                            faces_data.append({
                                "student_id": face.student_id,
                                "full_name": full_name,
                                "identified": face.identified,
                                "similarity": round(face.similarity, 3),
                                "bbox": face.bbox,
                                "landmarks": face.landmarks,
                            })
                        
                        if active_session:
                            await db.commit()

                    # Gửi kết quả nhận diện đầy đủ
                    await websocket.send_json({
                        "type": "recognition",
                        "frame_id": result.frame_id,
                        "processing_time_ms": round(result.processing_time_ms, 1),
                        "total_faces": result.total_faces,
                        "identified": result.identified_count,
                        "faces": faces_data,
                    })
            except asyncio.CancelledError:
                pass
            except RuntimeError as e:
                # Bỏ qua lỗi ngắt kết nối đột ngột của WebSocket
                if "close" not in str(e).lower() and "completed" not in str(e).lower():
                    logger.error(f"RuntimeError in background AI task: {e}")
            except Exception as e:
                logger.error(f"Error in background AI task: {e}")

        ai_task = None

        # Luồng lắng nghe lệnh từ Client (UI)
        async def listen_for_client():
            try:
                while True:
                    data = await websocket.receive_json()
                    # Không còn liveness commands
            except Exception:
                pass

        listen_task = asyncio.create_task(listen_for_client())

        while True:
            frame = video_capture.read()
            if frame is None:
                await asyncio.sleep(0.05)
                continue

            # 1. Gửi video frame
            jpeg_bytes = frame_processor.encode_frame_jpeg(frame, quality=75)
            await websocket.send_bytes(jpeg_bytes)

            # 2. Xử lý AI song song
            if ai_task is None or ai_task.done():
                ai_task = asyncio.create_task(process_and_send_result(frame))

            await asyncio.sleep(1.0 / 30)

    except WebSocketDisconnect:
        logger.info("WebSocket client đã ngắt kết nối")
    except Exception as e:
        # Bỏ qua dòng log WebSocket disconnect quá dài
        if "close" not in str(e).lower() and "completed" not in str(e).lower():
            logger.error(f"WebSocket error: {e}")
        try:
            await websocket.close()
        except:
            pass
    finally:
        if 'listen_task' in locals() and not listen_task.done():
            listen_task.cancel()
        if 'ai_task' in locals() and ai_task is not None and not ai_task.done():
            ai_task.cancel()
