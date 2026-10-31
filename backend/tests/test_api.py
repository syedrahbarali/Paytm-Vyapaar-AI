import pytest
import httpx
import pytest_asyncio
from app.main import app
from app.init_db import init_db

@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    from app.database import Base, engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await init_db()

@pytest.mark.asyncio
async def test_health_check():
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get("/")
    assert res.status_code == 200
    assert res.json()["status"] == "HEALTHY"

@pytest.mark.asyncio
async def test_dashboard_metrics():
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get("/api/v1/dashboard/metrics?merchant_id=sharma-kirana-001")
    assert res.status_code == 200
    data = res.json()
    assert data["merchant"]["business_name"] == "Sharma Kirana Store"
    assert data["today_summary"]["total_sales"] >= 9420.00
    assert data["khata_summary"]["total_pending_amount"] == 2250.00
    assert data["khata_summary"]["critical_count"] == 1
    assert data["loan_offer"]["pre_approved_amount"] == 50000.00

@pytest.mark.asyncio
async def test_khata_list_and_reminder():
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get("/api/v1/khata/list?merchant_id=sharma-kirana-001")
        assert res.status_code == 200
        entries = res.json()["entries"]
        assert len(entries) >= 2
        ramesh = next(e for e in entries if "Ramesh" in e["customer_name"])
        assert ramesh["amount_due"] == 1400.00

        # Send reminder
        remind_res = await ac.post("/api/v1/khata/send-reminder", json={"khata_id": ramesh["id"]})
        assert remind_res.status_code == 200
        assert remind_res.json()["status"] == "DELIVERED"
        assert "paytm.me" in remind_res.json()["payment_link"]

@pytest.mark.asyncio
async def test_loan_claim():
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.post("/api/v1/loan/claim", json={
            "merchant_id": "sharma-kirana-001",
            "amount": 50000.0,
            "otp_consent": "849201"
        })
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "DISBURSED"
    assert data["amount"] == 50000.00
    assert data["daily_sweep_amount"] == 300.00

@pytest.mark.asyncio
async def test_soundbox_webhook():
    import uuid
    random_key = f"TXN_{uuid.uuid4().hex[:8]}"
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.post("/api/v1/soundbox/webhook", json={
            "soundbox_device_id": "SB-DELHI-981",
            "idempotency_key": random_key,
            "amount": 150.0,
            "payer_name": "Test Customer",
            "payment_mode": "Paytm UPI"
        })
    assert res.status_code == 201
    data = res.json()
    assert data["status"] == "SUCCESS"
    assert "₹150" in data["soundbox_chime"]
