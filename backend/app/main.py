from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import os
import json
from pathlib import Path
from sqlalchemy import select, desc

from app.config import settings
from app.init_db import init_db
from app.database import AsyncSessionLocal, Merchant, KhataEntry
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

# Mount Jinja2 templates
templates_dir = Path("backend/app/templates")
templates = Jinja2Templates(directory=str(templates_dir))

# Mount API V1 routes
app.include_router(api_v1_router, prefix=settings.API_V1_STR)

@app.get("/checkout", response_class=RedirectResponse)
async def checkout_default():
    return RedirectResponse(url="/checkout/sharma-kirana-001")

@app.get("/checkout/{merchant_id}", response_class=HTMLResponse)
async def serve_customer_checkout(merchant_id: str, request: Request):
    async with AsyncSessionLocal() as session:
        merchant = await session.get(Merchant, merchant_id)
        if not merchant:
            merchant = await session.get(Merchant, "sharma-kirana-001")

        # Check for active pending khata for default demo customer (Rahul Kumar)
        res = await session.execute(
            select(KhataEntry)
            .where(KhataEntry.merchant_id == merchant.id, KhataEntry.status != "SETTLED")
            .order_by(desc(KhataEntry.amount_due))
            .limit(1)
        )
        khata = res.scalar_one_or_none()
        pending_json = json.dumps({
            "has_pending": khata is not None,
            "amount_due": float(khata.amount_due) if khata else 0.0,
            "days_overdue": khata.days_overdue if khata else 0,
            "customer_name": khata.customer_name if khata else "Rahul Kumar"
        })

    return templates.TemplateResponse(
        request=request,
        name="checkout.html",
        context={
            "merchant_id": merchant.id,
            "business_name": merchant.business_name,
            "soundbox_device_id": merchant.soundbox_device_id,
            "pending_khata_json": pending_json
        }
    )

@app.get("/")
def health_check():
    return {
        "service": "Paytm VyapaarAI Core Engine",
        "status": "HEALTHY",
        "version": settings.VERSION,
        "docs_url": "/docs",
        "customer_checkout_url": "/checkout/sharma-kirana-001",
        "counter_qr_url": "/api/v1/merchant/counter-qr"
    }
