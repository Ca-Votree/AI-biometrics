# 🧬 AI Biometrics - Hệ Thống Điểm Danh Bằng Nhận Diện Khuôn Mặt

Hệ thống điểm danh tự động sử dụng AI nhận diện khuôn mặt, được xây dựng cho hội trường / lớp học. 
Hệ thống đã được tách biệt hoàn toàn giữa Backend (FastAPI) và Frontend (HTML/JS/CSS) để dễ dàng triển khai (deploy) và phát triển độc lập.

## 🏗️ Kiến Trúc

```
Camera → Frame Extraction → Face Detection (SCRFD) → Face Alignment 
→ Feature Extraction (ArcFace-512d) → FAISS Vector Search → API Backend ↔ Frontend
```

## ⚡ Tech Stack

- **Backend**: FastAPI + WebSocket + SQLite (dev)
- **AI Models**: InsightFace SCRFD (Detection) + ArcFace (Recognition) + FAISS (Vector DB)
- **Frontend**: Vanilla HTML/CSS/JS (Giao tiếp qua REST API & WebSocket)

---

## 🚀 Cài đặt & Chạy (Local)

Hệ thống gồm 2 thành phần độc lập: **Backend** và **Frontend**. Bạn cần chạy cả 2 để sử dụng đầy đủ chức năng.

### 1. Khởi động Backend (Port 8000)

Sử dụng Anaconda/Miniconda (Khuyến nghị):

```bash
cd backend

# Tạo môi trường và cài dependencies
conda env create -f environment.yml

# Kích hoạt môi trường
conda activate biometrics

# Cấu hình biến môi trường
copy .env.example .env

# Chạy server FastAPI
python run.py
```
*Backend sẽ chạy tại: `http://localhost:8000`*

### 2. Khởi động Frontend (Live Server)

Frontend hiện tại là các file tĩnh (Static HTML/JS/CSS), đã được cấu hình trỏ tới `http://localhost:8000`. 
Để chạy frontend, bạn có thể dùng bất kỳ HTTP server tĩnh nào, ví dụ:

**Cách 1: Dùng VSCode Live Server Extension**
Mở thư mục `frontend/` trong VS Code, chuột phải vào `index.html` và chọn **"Open with Live Server"**.

**Cách 2: Dùng Python HTTP Server**
```bash
cd frontend
python -m http.server 5500
```
*Truy cập bảng điều khiển tại: `http://localhost:5500`*

---

## 📖 Hướng dẫn sử dụng

1. **Thêm sinh viên**: Vào trang Quản lý sinh viên → Thêm sinh viên mới
2. **Đăng ký khuôn mặt**: Upload ảnh khuôn mặt cho sinh viên
3. **Tạo phiên điểm danh**: Vào trang Điểm danh → Tạo phiên mới
4. **Bật camera**: Vào trang Giám sát Live → Bật Camera → Kết nối Stream
5. **Xem kết quả**: Theo dõi trực tiếp trên Dashboard hoặc chi tiết trong từng Phiên điểm danh.

## 📁 Cấu trúc dự án mới

```
├── backend/           # Thư mục xử lý logic & AI Model (FastAPI)
│   ├── app/           # Mã nguồn API & AI pipeline
│   ├── models/        # AI model weights
│   ├── data/          # Database (SQLite), FAISS index, Logs
│   ├── run.py         # Script khởi động server
│   ├── environment.yml# Môi trường Conda
│   └── requirements.txt
├── frontend/          # Thư mục giao diện người dùng
│   ├── static/        # CSS, JS, Images (nếu có)
│   ├── index.html     # Dashboard
│   ├── monitor.html   # Giao diện Camera Monitoring
│   ├── students.html  # Quản lý Sinh viên
│   └── attendance.html# Quản lý Điểm danh
└── README.md
```
## 👨‍💻 Tác giả

**Nguyễn Tuấn Vũ**

**Vai trò:**
- Trưởng nhóm phát triển
- Thiết kế kiến trúc hệ thống
- Phát triển Backend & Frontend
- Tích hợp AI
- Thiết kế cơ sở dữ liệu
- Triển khai hệ thống

---

## 🎓 Thông tin đề tài

Dự án được thực hiện trong khuôn khổ **đề tài nghiên cứu khoa học (NCKH)**, nghiên cứu và phát triển hệ thống điểm danh tự động sử dụng công nghệ nhận diện khuôn mặt dựa trên trí tuệ nhân tạo (AI).
## License

Dành cho nghiên cứu khoa học - Đề tài NCKH.
