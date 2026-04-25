"""In-memory session manager with auto-expiration."""

import asyncio
import os
import shutil
import tempfile
import time
from typing import Optional

from config import SESSION_EXPIRE_HOURS, SESSION_CLEANUP_INTERVAL


class SessionData:
    """Per-session data holder."""

    def __init__(self, session_id: str):
        self.session_id = session_id
        self.temp_dir = tempfile.mkdtemp(prefix=f"att_{session_id[:8]}_")
        self.created_at = time.time()
        self.last_access = time.time()

        # Uploaded file paths
        self.roster_path: Optional[str] = None
        self.attendance_paths: list[str] = []
        self.ledger_path: Optional[str] = None

        # Original file names (for display)
        self.roster_filename: Optional[str] = None
        self.attendance_filenames: list[str] = []
        self.ledger_filename: Optional[str] = None

        # Config
        self.late_tolerance: int = 10
        self.project_id: int = 1

        # Results
        self.salary_records: Optional[list[dict]] = None
        self.daily_records: Optional[list[dict]] = None
        self.overview: Optional[dict] = None
        self.sheet_name: Optional[str] = None
        self.abnormal_count: int = 0

        # Output files
        self.att_summary_path: Optional[str] = None
        self.ledger_output_path: Optional[str] = None
        self.report_path: Optional[str] = None

    def touch(self):
        self.last_access = time.time()

    def is_expired(self) -> bool:
        return (time.time() - self.last_access) > SESSION_EXPIRE_HOURS * 3600

    def cleanup(self):
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir, ignore_errors=True)


class SessionManager:
    """Singleton session manager."""

    def __init__(self):
        self._sessions: dict[str, SessionData] = {}
        self._cleanup_task: Optional[asyncio.Task] = None

    def start_cleanup(self):
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())

    async def _cleanup_loop(self):
        while True:
            await asyncio.sleep(SESSION_CLEANUP_INTERVAL)
            expired = [sid for sid, s in self._sessions.items() if s.is_expired()]
            for sid in expired:
                self._sessions[sid].cleanup()
                del self._sessions[sid]

    def create_session(self) -> SessionData:
        import uuid
        session_id = uuid.uuid4().hex
        data = SessionData(session_id)
        self._sessions[session_id] = data
        return data

    def get_session(self, session_id: str) -> Optional[SessionData]:
        data = self._sessions.get(session_id)
        if data:
            data.touch()
        return data

    def delete_session(self, session_id: str) -> bool:
        data = self._sessions.pop(session_id, None)
        if data:
            data.cleanup()
            return True
        return False


# Global singleton
session_manager = SessionManager()
