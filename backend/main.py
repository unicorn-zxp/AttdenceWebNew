"""FastAPI main application."""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from services.session_manager import session_manager
from config import HOST, PORT

# Import routers
from routers.upload import router as upload_router
from routers.calculate import router as calculate_router
from routers.results import router as results_router
from routers.download import router as download_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: start session cleanup task
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


# Session endpoints
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
async def update_config(session_id: str = Query(...), late_tolerance: int = 10):
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(404, "会话不存在")
    session.late_tolerance = late_tolerance
    return {"status": "ok", "late_tolerance": late_tolerance}


@app.get("/api/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=HOST, port=PORT)
