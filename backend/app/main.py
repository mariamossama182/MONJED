import sys
from pathlib import Path

# Repo root (parent of backend/) so top-level AI/ package imports resolve.
_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.community_reports import router as community_reports_router
from app.routers.flood import router as flood_router
from app.routers.earthquake import router as earthquake_router
from app.routers.test_ui import router as test_ui_router
from app.routers.decision import router as decision_router
from app.routers.pipeline import router as pipeline_router
from app.routers.assistance import router as assistance_router
from app.routers.accessibility import router as accessibility_router
from app.routers.dashboard import router as dashboard_router
from app.routers.auth import router as auth_router
from app.routers import users


@asynccontextmanager
async def lifespan(_app: FastAPI):
    try:
        from database.indexes import create_indexes

        create_indexes()
        print("MONJED Mongo indexes ready")
    except Exception as exc:
        print(f"MONJED Mongo indexes skipped: {type(exc).__name__}: {exc}")
    yield


app = FastAPI(
    title="MONJED API",
    description=(
        "AI-powered disaster risk interpretation "
        "and action support platform"
    ),
    version="0.1.0",
    lifespan=lifespan,
)


# ============================================================
# CORS
# ============================================================

# Local frontend development origins.
# Vite usually uses port 5173.
# React/Next development may use port 3000.
allowed_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# ROUTERS
# ============================================================

app.include_router(flood_router)
app.include_router(earthquake_router)
app.include_router(community_reports_router)
app.include_router(decision_router)
app.include_router(pipeline_router)
app.include_router(assistance_router)
app.include_router(accessibility_router)
app.include_router(test_ui_router)
app.include_router(dashboard_router)
app.include_router(users.router)
app.include_router(auth_router)


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():
    return {
        "message": "Welcome to MONJED API",
        "service": "MONJED API",
        "status": "running",
    }


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "MONJED API",
    }
