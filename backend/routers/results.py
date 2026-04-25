"""Results API routes - salary and daily data queries."""

from fastapi import APIRouter, Query, HTTPException

from services.session_manager import session_manager

router = APIRouter(prefix="/api/results", tags=["results"])


@router.get("/salary")
async def get_salary(session_id: str = Query(...)):
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(404, "会话不存在")

    if session.salary_records is None:
        raise HTTPException(400, "请先执行计算")

    return {
        "overview": session.overview,
        "records": session.salary_records,
        "sheet_name": session.sheet_name,
    }


@router.get("/daily")
async def get_daily(session_id: str = Query(...)):
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(404, "会话不存在")

    if session.daily_records is None:
        raise HTTPException(400, "请先执行计算")

    return {"records": session.daily_records}
