
import os
import numpy as np
from loguru import logger
from app.config import settings

try:
    from ultralytics import YOLO
except ImportError:
    logger.warning("ultralytics chưa được cài đặt. Chạy: pip install ultralytics")
    YOLO = None


class Face:

    def __init__(self, bbox, det_score, kps=None):
        self.bbox = np.array(bbox)
        self.det_score = det_score
        self.kps = np.array(kps) if kps is not None else None
        self.embedding = None 


class FaceDetector:


    def __init__(self):
        self._model = None
        self._initialized = False

    def initialize(self):
        """Khởi tạo model YOLO."""
        if self._initialized:
            return

        if YOLO is None:
            raise ImportError("Chạy: pip install ultralytics để cài đặt thư viện")

        model_path = os.path.join(settings.MODELS_DIR, "yolov8n-face.pt")
        
        logger.info(f"Đang tải model YOLO từ: {model_path}")
        self._model = YOLO(model_path)

        # Chuyển model sang CPU
        device = 'cpu'
        self._model.to(device)
        
        self._initialized = True
        logger.info(f"✅ Model YOLO phát hiện khuôn mặt đã sẵn sàng trên thiết bị: CPU")

    def detect(self, frame: np.ndarray) -> list:
        """
        Phát hiện khuôn mặt trong frame sử d YOLO.
        """
        if not self._initialized:
            self.initialize()

        # result is a list of Results objects
        results = self._model(frame, verbose=False, conf=settings.FACE_DETECTION_THRESHOLD)
        faces = []
        
        for r in results:
            boxes = r.boxes
            for box in boxes:
                # bounding box
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                score = box.conf[0].cpu().item()
                
                # keypoints (nếu sử dụng model hỗ trợ)
                kps = None
                if getattr(r, 'keypoints', None) is not None:
                    kps_data = r.keypoints.xy[0].cpu().numpy()
                    if len(kps_data) >= 5:
                        kps = kps_data[:5]
                
                faces.append(Face(bbox=[x1, y1, x2, y2], det_score=score, kps=kps))
        
        # Giới hạn số lượng khuôn mặt
        if len(faces) > settings.MAX_FACES_PER_FRAME:
            faces = sorted(faces, key=lambda x: x.det_score, reverse=True)
            faces = faces[:settings.MAX_FACES_PER_FRAME]
        
        logger.debug(f"YOLO phát hiện {len(faces)} khuôn mặt trong frame")
        return faces

    def detect_batch(self, frames: list[np.ndarray]) -> list[list]:
        return [self.detect(frame) for frame in frames]

    @staticmethod
    def extract_face_data(face) -> dict:
        data = {
            "bbox": face.bbox.astype(int).tolist(),
            "landmarks": face.kps.tolist() if face.kps is not None else None,
            "score": float(face.det_score),
        }
        if face.embedding is not None:
            data["embedding"] = face.embedding.tolist()
        return data

    @property
    def is_initialized(self) -> bool:
        return self._initialized

    def release(self):
        """Giải phóng tài nguyên."""
        self._model = None
        self._initialized = False
        logger.info("YOLO Face detector đã được giải phóng")


# Singleton instance
face_detector = FaceDetector()
