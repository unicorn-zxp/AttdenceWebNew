"""Upload API routes."""

import asyncio
import os
import shutil

from fastapi import APIRouter, UploadFile, File, HTTPException, Query

from services.session_manager import session_manager
from database import seed_from_ledger
from config import ALLOWED_EXTENSIONS

router = APIRouter(prefix="/api/upload", tags=["upload"])


def _validate_ext(filename: str, allowed: set[str]) -> str:
    _, ext = os.path.splitext(filename.lower())
    if ext not in allowed:
        raise HTTPException(400, f"不支持的文件类型: {ext}，允许: {allowed}")
    return ext


@router.post("/roster")
async def upload_roster(session_id: str = Query(...), file: UploadFile = File(...)):
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(404, "会话不存在")

    ext = _validate_ext(file.filename, ALLOWED_EXTENSIONS["roster"])
    dest = os.path.join(session.temp_dir, f"roster{ext}")
    with open(dest, "wb") as f:
        shutil.copyfileobj(file.file, f)
    session.roster_path = dest
    session.roster_filename = file.filename
    return {"status": "ok", "filename": file.filename}


@router.post("/attendance")
async def upload_attendance(session_id: str = Query(...), files: list[UploadFile] = File(...)):
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(404, "会话不存在")

    paths = []
    names = []
    for i, file in enumerate(files):
        ext = _validate_ext(file.filename, ALLOWED_EXTENSIONS["attendance"])
        dest = os.path.join(session.temp_dir, f"员工刷卡记录表{i+1}{ext}")
        with open(dest, "wb") as f:
            shutil.copyfileobj(file.file, f)
        paths.append(dest)
        names.append(file.filename)
    session.attendance_paths = paths
    session.attendance_filenames = names
    return {"status": "ok", "count": len(files)}


@router.post("/ledger")
async def upload_ledger(
    session_id: str = Query(...),
    project_id: int = Query(default=1),
    file: UploadFile = File(...),
):
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(404, "会话不存在")

    ext = _validate_ext(file.filename, ALLOWED_EXTENSIONS["ledger"])
    dest = os.path.join(session.temp_dir, f"工资台账{ext}")
    with open(dest, "wb") as f:
        shutil.copyfileobj(file.file, f)
    session.ledger_path = dest
    session.ledger_filename = file.filename
    session.project_id = project_id

    # Seed historical monthly data from existing ledger sheets
    try:
        count = await asyncio.to_thread(seed_from_ledger, project_id, dest)
    except Exception:
        count = 0

    return {"status": "ok", "filename": file.filename, "seeded_months": count}


@router.get("/status")
async def upload_status(session_id: str = Query(...)):
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(404, "会话不存在")

    return {
        "roster": session.roster_path is not None,
        "attendance": len(session.attendance_paths) > 0,
        "ledger": session.ledger_path is not None,
        "attendance_count": len(session.attendance_paths),
        "project_id": getattr(session, "project_id", 1),
        "roster_filename": session.roster_filename,
        "attendance_filenames": session.attendance_filenames,
        "ledger_filename": session.ledger_filename,
    }
