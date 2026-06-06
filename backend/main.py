"""FastAPI main application."""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from services.session_manager import session_manager
from database import init_db, get_annual, list_projects, create_project, delete_project
from config import HOST, PORT

# Import routers
from routers.upload import router as upload_router
from routers.calculate import router as calculate_router
from routers.results import router as results_router
from routers.download import router as download_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: init database + start session cleanup
    init_db()
    session_manager.start_cleanup()
    yield
    # Shutdown: cleanup all sessions
    for sid in list(session_manager._sessions.keys()):
        session_manager.delete_session(sid)


app = FastAPI(
    title="工地考勤工资计算系统 API",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(upload_router)
app.include_router(calculate_router)
app.include_router(results_router)
app.include_router(download_router)


# ─── Session endpoints ─────────────────────────────────────

@app.post("/api/session")
async def create_session():
    data = session_manager.create_session()
    return {"session_id": data.session_id}


@app.delete("/api/session/{session_id}")
async def delete_session(session_id: str):
    if not session_manager.delete_session(session_id):
        raise HTTPException(404, "会话不存在")
    return {"status": "ok"}


@app.put("/api/config")
async def update_config(
    session_id: str = Query(...),
    late_tolerance: int = 10,
    work_start_time: str = "07:30",
    work_end_time: str = "17:30",
    break_start: str = "12:00",
    break_end: str = "13:00",
):
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(404, "会话不存在")
    session.late_tolerance = late_tolerance
    session.work_start_time = work_start_time
    session.work_end_time = work_end_time
    session.break_start = break_start
    session.break_end = break_end
    return {
        "status": "ok",
        "late_tolerance": late_tolerance,
        "work_start_time": work_start_time,
        "work_end_time": work_end_time,
        "break_start": break_start,
        "break_end": break_end,
    }


@app.get("/api/health")
async def health():
    return {"status": "ok"}


# ─── Project endpoints ─────────────────────────────────────

@app.get("/api/projects")
async def api_list_projects():
    """List all projects."""
    return {"projects": list_projects()}


@app.post("/api/projects")
async def api_create_project(name: str = Query(..., min_length=1)):
    """Create a new project."""
    return create_project(name)


@app.delete("/api/projects/{project_id}")
async def api_delete_project(project_id: int):
    """Delete a project and all its data."""
    if not delete_project(project_id):
        raise HTTPException(404, "项目不存在")
    return {"status": "ok"}


# ─── Annual summary (project-scoped) ───────────────────────

@app.get("/api/annual-summary")
async def annual_summary(
    project_id: int = Query(default=1),
    year: int = Query(default=2026),
):
    """Public endpoint — no session required. Returns monthly summaries from DB."""
    months = get_annual(project_id, year)
    return {"year": year, "project_id": project_id, "months": months}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=HOST, port=PORT)
