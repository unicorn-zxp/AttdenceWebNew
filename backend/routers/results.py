"""Results API routes - salary and daily data queries."""

from fastapi import APIRouter, Query, HTTPException

from services.session_manager import session_manager
from database import get_annual, load_calculation, list_calculations

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


@router.get("/history")
async def get_history(
    project_id: int = Query(default=1),
    year: int = Query(...),
    month: int = Query(...),
):
    """Load a previously calculated month's full results from DB.
    This works even if the session has expired."""
    result = load_calculation(project_id, year, month)
    if not result:
        raise HTTPException(404, "该月份数据不存在")
    return {
        "overview": result["overview"],
        "salary_records": result["salary_records"],
        "daily_records": result["daily_records"],
        "sheet_name": result["sheet_name"],
        "abnormal_count": result["abnormal_count"],
    }


@router.get("/history-list")
async def get_history_list(project_id: int = Query(default=1)):
    """List all saved calculation results for a project."""
    return {"calculations": list_calculations(project_id)}
