"""
CloudGuard AI – FastAPI Application Entry Point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os

from app.config import settings
from app.database import connect_db, close_db
from app.routes.auth import router as auth_router
from app.routes.aws import router as aws_router
from app.routes.scan import router as scan_router
from app.routes.report import router as report_router
from app.routes.alerts import router as alerts_router
from app.routes.admin import router as admin_router


# ── Lifespan (startup / shutdown) ─────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_db()
    # Ensure reports directory exists
    os.makedirs("reports", exist_ok=True)
    yield
    await close_db()


# ── App Instance ──────────────────────────────────────────────────────────────
app = FastAPI(
    title="CloudGuard AI",
    description="AWS Cloud Security Monitoring and Threat Detection System",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan,
)

# ── CORS ──────────────────────────────────────────────────────────────────────
allowed_origins = [origin.strip() for origin in settings.CORS_ORIGINS.split(",") if origin.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(auth_router)
app.include_router(aws_router)
app.include_router(scan_router)
app.include_router(report_router)
app.include_router(alerts_router)
app.include_router(admin_router)

# ── Health Check ──────────────────────────────────────────────────────────────
@app.get("/api/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": "1.0.0",
        "demo_mode": settings.DEMO_MODE,
    }


@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "Welcome to CloudGuard AI API",
        "docs": "/api/docs",
        "health": "/api/health",
    }
