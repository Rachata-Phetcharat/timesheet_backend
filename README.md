# 🕒 Timesheet Backend API (FastAPI)

ระบบ API สำหรับจัดการเวลาทำงาน (Timesheet), บันทึกเวลาเข้า-ออกงาน (Attendance Tracking), และยื่นคำขอลา (Leave Requests) พัฒนาด้วย **FastAPI**, **SQLAlchemy 2.0 (Async)**, **PostgreSQL**, **Alembic**, และ **Pydantic v2**

---

## 🏗️ สถาปัตยกรรมของระบบ (Architecture)

โปรเจกต์นี้ออกแบบโครงสร้างตามรูปแบบ **3-Tier Layer Architecture** (Route → Service → Repository) เพื่อแยกหน้าที่ความรับผิดชอบ (Separation of Concerns) ให้โค้ดดูแลรักษาง่ายและทดสอบได้สะดวก:

1. **API / Route Layer (`app/api/`)**: จัดการ HTTP Request/Response, Validation, Serializer, และ Authentication Dependency
2. **Service Layer (`app/services/`)**: Business Logic ทั้งหมด เช่น การคำนวณการมาสาย (Late Calculation), การสรุปสถิติประจำเดือน, การตรวจสอบสิทธิ์การอนุมัติคำขอลา
3. **Repository Layer (`app/repositories/`)**: การติดต่อสื่อสารและ Query ฐานข้อมูลผ่าน SQLAlchemy Async ORM โดยเฉพาะ

```
[ HTTP Request ]
       ↓
[ FastAPI Route Handler (app/api/routes) ]
       ↓
[ Service Object (app/services) ]  <-- Business Logic (เช่น คำนวณเวลาสาย)
       ↓
[ Repository Layer (app/repositories) ] <-- DB Queries / Transactions
       ↓
[ PostgreSQL Database ]
```

---

## 🛠️ Tech Stack

- **Framework**: FastAPI (v0.115+)
- **ASGI Server**: Uvicorn
- **ORM**: SQLAlchemy 2.0 (Async Engine)
- **Database Driver**: `asyncpg`
- **Database**: PostgreSQL 16
- **Database Migrations**: Alembic
- **Validation & Serialization**: Pydantic v2 / Pydantic Settings
- **Authentication**: JWT (`python-jose`) + `bcrypt`
- **Testing**: Pytest, `pytest-asyncio`, `httpx`, `aiosqlite`
- **Containerization**: Docker & Docker Compose

---

## 📁 โครงสร้างโปรเจกต์ (Project Structure)

```
timesheet-backend/
├── app/
│   ├── main.py                        # FastAPI app entrypoint + CORS + Router registration
│   ├── seed.py                        # Script สำหรับสร้างบัญชีเริ่มต้น (Admin/Staff)
│   ├── core/
│   │   ├── config.py                  # Pydantic Settings อ่านค่าจาก .env
│   │   ├── security.py                # JWT encode/decode, bcrypt hashing
│   │   └── database.py                # Async engine & sessionmaker
│   ├── models/                        # SQLAlchemy Database Models
│   │   ├── employee.py                # Employee Model & Role Enum (staff, admin)
│   │   ├── attendance.py              # AttendanceRecord Model & Status Enum
│   │   └── leave_request.py           # LeaveRequest Model, LeaveType & LeaveStatus
│   ├── schemas/                       # Pydantic Request/Response Models
│   │   ├── auth.py                    # LoginRequest, Token, RefreshTokenRequest
│   │   ├── employee.py                # EmployeeBase, EmployeeCreate, EmployeeResponse
│   │   ├── attendance.py              # ClockInResponse, ClockOutResponse, MonthlySummary
│   │   └── leave_request.py           # LeaveRequestCreate, LeaveStatusUpdate, Response
│   ├── api/
│   │   ├── deps.py                    # get_db, get_current_user, get_current_admin
│   │   └── routes/
│   │       ├── auth.py                # /auth/login, /auth/refresh, /auth/me
│   │       ├── attendance.py          # /attendance/me, /attendance/clock-in, /clock-out
│   │       └── leave_requests.py      # /leave-requests CRUD & status approval
│   ├── services/                      # Business Logic
│   │   ├── attendance_service.py      # Logic คำนวณสาย และสรุปสถิติประจำเดือน
│   │   └── leave_service.py           # Logic ยื่นใบลาและตรวจสอบสิทธิ์
│   └── repositories/                  # DB Query Layer
│       ├── employee_repo.py           # Database operations for Employees
│       ├── attendance_repo.py         # Database operations for Attendance
│       └── leave_repo.py              # Database operations for Leave Requests
├── alembic/                           # Database Migrations
│   ├── versions/
│   │   └── 001_initial_tables.py      # Migration สร้างตารางเริ่มต้น
│   └── env.py                         # Async Alembic runner
├── tests/                             # Automated Tests
│   ├── conftest.py                    # In-memory test DB + async fixtures
│   ├── test_auth.py                   # Tests สำหรับระบบ Authentication
│   ├── test_attendance.py             # Tests สำหรับระบบบันทึกเวลาทำงาน
│   └── test_leave_requests.py         # Tests สำหรับระบบการลา
├── .env / .env.example                # Environment variables
├── alembic.ini                        # Alembic configuration
├── Dockerfile                         # Dockerfile สำหรับ Backend
├── docker-compose.yml                 # Docker Compose (PostgreSQL + Backend)
├── pytest.ini                         # Pytest configuration
└── requirements.txt                   # รายการ Python dependencies
```

---

## 🚀 การติดตั้งและเริ่มต้นใช้งาน (Getting Started)

### วิธีที่ 1: รันด้วย Docker Compose (แนะนำ)

1. คัดลอกไฟล์ `.env`:
   ```bash
   cp .env.example .env
   ```
2. เริ่มต้นระบบทั้งหมดด้วย Docker Compose:
   ```bash
   docker compose up --build -d
   ```
3. รัน Migration และ Seed ข้อมูลเริ่มต้นใน Backend container:
   ```bash
   docker compose exec backend alembic upgrade head
   docker compose exec backend python -m app.seed
   ```
4. เปิดดู Swagger UI: `http://localhost:8000/docs`

---

### วิธีที่ 2: รันแบบ Local Development (Python Virtualenv)

#### 1. สร้างและเปิดใช้งาน Virtual Environment
```bash
# macOS / Linux
python3 -m venv venv
source venv/bin/activate

# Windows (PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1
```

#### 2. ติดตั้ง Dependencies
```bash
pip install -r requirements.txt
```

#### 3. สตาร์ท PostgreSQL Database (ผ่าน Docker)
```bash
docker compose up -d db
```

#### 4. ตั้งค่า Environment Variables
ไฟล์ `.env`:
```env
DATABASE_URL=postgresql+asyncpg://timesheet:timesheet@localhost:5433/timesheet
SECRET_KEY=timesheet-secret-key-change-in-production-2026-secure-jwt
DEBUG=True
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7
```

#### 5. รัน Database Migration
```bash
alembic upgrade head
```

#### 6. Seed ข้อมูลผู้ใช้เริ่มต้น
```bash
python -m app.seed
```

#### 7. รัน Development Server
```bash
uvicorn app.main:app --reload --port 8000
```
- Swagger UI (OpenAPI): [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 👥 บัญชีผู้ใช้เริ่มต้นสำหรับทดสอบ (Seed Accounts)

| Email | Password | Role | Full Name |
| :--- | :--- | :--- | :--- |
| `admin@timesheet.local` | `admin1234` | `admin` | System Admin |
| `staff@timesheet.local` | `staff1234` | `staff` | Staff Employee |

---

## 📑 สรุปรายการ API Endpoints

### 1. Authentication (`/auth`)

#### `POST /auth/login`
เข้าสู่ระบบเพื่อรับ JWT Access Token และ Refresh Token
- **Request Body**:
  ```json
  {
    "email": "staff@timesheet.local",
    "password": "staff1234"
  }
  ```
- **Response (200 OK)**:
  ```json
  {
    "access_token": "eyJhbGciOi...",
    "refresh_token": "eyJhbGciOi...",
    "token_type": "bearer"
  }
  ```

#### `POST /auth/refresh`
ขอรับ Token ชุดใหม่ด้วย Refresh Token
- **Request Body**:
  ```json
  {
    "refresh_token": "eyJhbGciOi..."
  }
  ```
- **Response (200 OK)**:
  ```json
  {
    "access_token": "eyJhbGciOi...",
    "refresh_token": "eyJhbGciOi...",
    "token_type": "bearer"
  }
  ```

#### `GET /auth/me`
ดูข้อมูลผู้ใช้ปัจจุบัน (ต้องการ Header `Authorization: Bearer <token>`)
- **Response (200 OK)**:
  ```json
  {
    "id": "9c87c77b-5774-48be-824d-f6fc700daf5b",
    "email": "staff@timesheet.local",
    "full_name": "Staff Employee",
    "role": "staff"
  }
  ```

---

### 2. Attendance (`/attendance`)

#### `POST /attendance/clock-in`
บันทึกเวลาเข้างานของวันปัจจุบัน (คำนวณสายอัตโนมัติหากเข้างานหลัง 09:00)
- **Response (200 OK)**:
  ```json
  {
    "id": "e3a89045-812e-4b62-9721-a3f169f45678",
    "employee_id": "9c87c77b-5774-48be-824d-f6fc700daf5b",
    "clock_in_at": "2026-08-25T08:55:00+07:00",
    "clock_out_at": null,
    "status": "on_time",
    "late_minutes": 0
  }
  ```

#### `POST /attendance/clock-out`
บันทึกเวลาออกงานของวันปัจจุบัน
- **Response (200 OK)**:
  ```json
  {
    "id": "e3a89045-812e-4b62-9721-a3f169f45678",
    "employee_id": "9c87c77b-5774-48be-824d-f6fc700daf5b",
    "clock_in_at": "2026-08-25T08:55:00+07:00",
    "clock_out_at": "2026-08-25T18:00:00+07:00",
    "status": "on_time",
    "late_minutes": 0
  }
  ```

#### `GET /attendance/me?month=YYYY-MM`
ดูรายการประวัติและสรุปสถิติประจำเดือนของผู้ใช้
- **Query Parameter**: `month` (Optional เช่น `2026-08`, หากไม่ระบุจะแสดงเดือนปัจจุบัน)
- **Response (200 OK)**:
  ```json
  {
    "month": "2026-08",
    "total_days": 20,
    "on_time_count": 18,
    "late_count": 2,
    "absent_count": 0,
    "total_late_minutes": 45,
    "records": [
      {
        "id": "e3a89045-812e-4b62-9721-a3f169f45678",
        "employee_id": "9c87c77b-5774-48be-824d-f6fc700daf5b",
        "clock_in_at": "2026-08-25T08:55:00+07:00",
        "clock_out_at": "2026-08-25T18:00:00+07:00",
        "status": "on_time",
        "late_minutes": 0
      }
    ]
  }
  ```

---

### 3. Leave Requests (`/leave-requests`)

#### `GET /leave-requests/me`
ดึงรายการคำขอลาทั้งหมดของตนเอง
- **Response (200 OK)**:
  ```json
  [
    {
      "id": "f51b9e31-561b-4395-8162-d27838561729",
      "employee_id": "9c87c77b-5774-48be-824d-f6fc700daf5b",
      "type": "sick",
      "start_date": "2026-08-26",
      "end_date": "2026-08-27",
      "reason": "Doctor appointment",
      "status": "pending",
      "employee": null
    }
  ]
  ```

#### `POST /leave-requests`
ยื่นคำขอลาใหม่
- **Request Body**:
  ```json
  {
    "type": "personal",
    "start_date": "2026-08-28",
    "end_date": "2026-08-28",
    "reason": "Personal errands"
  }
  ```
- **Response (201 Created)**: คืนค่า Leave Request Object ที่สถานะเป็น `pending`

#### `GET /leave-requests/{id}`
ดูรายละเอียดคำขอลาตาม ID (เข้าถึงได้เฉพาะเจ้าของคำขอ หรือ Admin)
- **Response (200 OK)**: คืนค่า Leave Request Object

#### `PATCH /leave-requests/{id}/status`
อัปเดตสถานะคำขอลา (**เฉพาะ Admin เท่านั้น**)
- **Request Body**:
  ```json
  {
    "status": "approved"
  }
  ```
- **Response (200 OK)**:
  ```json
  {
    "id": "f51b9e31-561b-4395-8162-d27838561729",
    "employee_id": "9c87c77b-5774-48be-824d-f6fc700daf5b",
    "type": "sick",
    "start_date": "2026-08-26",
    "end_date": "2026-08-27",
    "reason": "Doctor appointment",
    "status": "approved",
    "employee": null
  }
  ```

---

## 🧪 การรัน Automated Test

ระบบมาพร้อมกับชุดทดสอบแบบครอบคลุม (Integration Tests) โดยใช้ In-Memory SQLite และ Async Client:

```bash
pytest -v
```

---

## 🔒 Security & Validation Details

- **Password Hashing**: เข้ารหัสด้วย `bcrypt`
- **Token Format**: Standard JWT Bearer (HS256)
- **Role-Based Access Control (RBAC)**: แยกสิทธิ์การทำงานระหว่าง `staff` และ `admin` ชัดเจนในระดับ Dependency (`get_current_admin`)
- **Data Validation**: ตรวจสอบความถูกต้องของ Input ด้วย Pydantic v2 เช่น วันที่สิ้นสุดการลาต้องไม่เกิดขึ้นก่อนวันที่เริ่มต้น (`end_date >= start_date`)
