import subprocess
import time
import os
import sys

def run_all():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.join(root_dir, "backend")
    frontend_dir = os.path.join(root_dir, "frontend")

    print("🚀 Đang khởi động AI Biometrics Attendance System...")

    # 1. Khởi động Backend
    print("📦 Đang khởi động Backend (FastAPI)...")
    backend_process = subprocess.Popen(
        [sys.executable, "run.py"],
        cwd=backend_dir
    )

    # Đợi một chút để backend sẵn sàng
    time.sleep(3)

    # 2. Khởi động Frontend
    print("🌐 Đang khởi động Frontend (HTTP Server trên port 3000)...")
    frontend_process = subprocess.Popen(
        [sys.executable, "-m", "http.server", "3000"],
        cwd=frontend_dir
    )

    print("\n✅ Hệ thống đã sẵn sàng!")
    print(f"🔗 Backend API: http://localhost:8000")
    print(f"🔗 Frontend: http://localhost:3000")
    print("\nNhấn Ctrl+C để dừng cả hai.\n")

    try:
        # Giữ script chạy để theo dõi các process
        while True:
            if backend_process.poll() is not None:
                print("❌ Backend đã dừng đột ngột.")
                break
            if frontend_process.poll() is not None:
                print("❌ Frontend đã dừng đột ngột.")
                break
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Đang dừng hệ thống...")
    finally:
        backend_process.terminate()
        frontend_process.terminate()
        print("Done.")

if __name__ == "__main__":
    run_all()
