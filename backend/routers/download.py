"""Download API routes - Excel file downloads."""

import os

from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import FileResponse

from services.session_manager import session_manager

router = APIRouter(prefix="/api/download", tags=["download"])


@router.get("/attendance-summary")
async def download_attendance_summary(session_id: str = Query(...)):
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(404, "会话不存在")

    if not session.att_summary_path or not os.path.exists(session.att_summary_path):
        raise HTTPException(400, "请先执行计算")

    return FileResponse(
        session.att_summary_path,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename="考勤记录汇总.xlsx",
    )


@router.get("/ledger")
async def download_ledger(session_id: str = Query(...)):
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(404, "会话不存在")

    if not session.ledger_output_path or not os.path.exists(session.ledger_output_path):
        raise HTTPException(400, "请先执行计算")

    return FileResponse(
        session.ledger_output_path,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename="工资台账2026（超）.xlsx",
    )


@router.get("/report")
async def download_report(session_id: str = Query(...)):
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(404, "会话不存在")

    if not session.report_path or not os.path.exists(session.report_path):
        raise HTTPException(400, "请先执行计算")

    filename = os.path.basename(session.report_path)
    return FileResponse(
        session.report_path,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=filename,
    )
