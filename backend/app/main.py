from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from pathlib import Path

from app.config import settings
from app.init_db import init_db
from app.api.v1.routes import router as api_v1_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB schema & seed data
    await init_db()
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Backend AI Engine & Soundbox Ledger for Paytm VyapaarAI",
    lifespan=lifespan
)

# Enable CORS for Android emulator, Web & Local devices
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for generated TTS audio replies
static_dir = Path("backend/static")
static_dir.mkdir(parents=True, exist_ok=True)
(static_dir / "audio").mkdir(parents=True, exist_ok=True)

app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Mount API V1 routes
app.include_router(api_v1_router, prefix=settings.API_V1_STR)

@app.get("/")
def health_check():
    return {
        "service": "Paytm VyapaarAI Core Engine",
        "status": "HEALTHY",
        "version": settings.VERSION,
        "docs_url": "/docs"
    }
