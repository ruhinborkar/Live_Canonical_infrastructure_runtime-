import asyncio
import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.api.routes import events, health, runs  # noqa: E402
from backend.api.websocket import register_observer, websocket_endpoint  # noqa: E402

app = FastAPI(
    title="Canonical Infrastructure Runtime API",
    description="Production API for deterministic runtime execution, replay, and recovery",
    version="1.0.0",
)

_dev_origins = [
    f"http://{host}:{port}"
    for host in ("localhost", "127.0.0.1")
    for port in range(5173, 5185)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_dev_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api")
app.include_router(runs.router, prefix="/api")
app.include_router(events.router, prefix="/api")
app.add_api_websocket_route("/ws", websocket_endpoint)

STATIC_DIR = ROOT / "backend" / "static"
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.on_event("startup")
async def startup() -> None:
    register_observer(asyncio.get_event_loop())


@app.get("/")
def root():
    dashboard = STATIC_DIR / "index.html"
    if dashboard.exists():
        return FileResponse(dashboard)
    return {
        "service": "Canonical Infrastructure Runtime",
        "docs": "/docs",
        "health": "/api/health",
    }
