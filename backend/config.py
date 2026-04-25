"""Backend configuration constants."""

import os

# Server
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))

# Attendance core module path (volume-mounted from ../attendance)
ATTENDANCE_CORE_DIR = os.getenv("ATTENDANCE_CORE_DIR", "/app/attendance")

# Session
SESSION_EXPIRE_HOURS = int(os.getenv("SESSION_EXPIRE_HOURS", "2"))
SESSION_CLEANUP_INTERVAL = int(os.getenv("SESSION_CLEANUP_INTERVAL", "3600"))  # seconds

# Upload
MAX_UPLOAD_SIZE = 50 * 1024 * 1024  # 50MB
ALLOWED_EXTENSIONS = {
    "roster": {".xlsx"},
    "attendance": {".xls", ".xlsx"},
    "ledger": {".xlsx"},
}
