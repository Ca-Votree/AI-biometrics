@echo off
echo 🚀 Khoi dong AI Biometrics Attendance System...

:: Khoi dong Backend trong cua so moi
echo 📦 Dang khoi dong Backend (FastAPI)...
start "Backend (Uvicorn)" cmd /c "cd backend && python run.py"

:: Khoi dong Frontend trong cua so moi
echo 🌐 Dang khoi dong Frontend (HTTP Server)...
start "Frontend (Server)" cmd /c "cd frontend && python -m http.server 3000"

echo.
echo ✅ He thong da khoi dong xong!
echo 🔗 Backend API: http://localhost:8000
echo 🔗 Frontend: http://localhost:3000
echo.
pause
