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
async def test_customer_checkout_html_page():
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get("/checkout/sharma-kirana-001")
    assert res.status_code == 200
    assert "text/html" in res.headers["content-type"]
    assert "Sharma Kirana Store" in res.text
    assert "SB-DELHI-981" in res.text
    assert "Pay via UPI" in res.text
    assert "Take Khata (Pay Later)" in res.text

@pytest.mark.asyncio
async def test_customer_checkout_details_json():
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get("/api/v1/customer/checkout-details/sharma-kirana-001?customer_phone=+919876543210")
    assert res.status_code == 200
    data = res.json()
    assert data["merchant_id"] == "sharma-kirana-001"
    assert data["business_name"] == "Sharma Kirana Store"
    # Ramesh has 1400 pending
    assert data["pending_khata"]["has_pending"] is True
    assert data["pending_khata"]["amount_due"] == 1400.00

@pytest.mark.asyncio
async def test_customer_pay_later_workflow():
    """Customer scans QR at counter and selects Pay-Later for ₹200."""
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.post("/api/v1/customer/pay-later", json={
            "merchant_id": "sharma-kirana-001",
            "customer_name": "Rahul Kumar",
            "customer_phone": "+919811223344",
            "amount": 200.0,
            "notes": "Evening milk & butter"
        })
    assert res.status_code == 201
    data = res.json()
    assert data["status"] == "RECORDED"
    assert data["amount"] == 200.0
    assert data["customer_name"] == "Rahul Kumar"
    assert "Sharma Kirana alert: Rahul Kumar ne 200 rupaye ka udhaar darj kiya!" in data["soundbox_announcement"]
    assert data["khata_id"].startswith("khata_qr_")

    # Verify that this khata entry is now visible in the merchant's khata list
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as ac:
        khata_res = await ac.get("/api/v1/khata/list?merchant_id=sharma-kirana-001")
    assert khata_res.status_code == 200
    entries = khata_res.json()["entries"]
    rahul_entry = next((e for e in entries if e["customer_name"] == "Rahul Kumar"), None)
    assert rahul_entry is not None
    assert rahul_entry["amount_due"] == 200.0
    assert rahul_entry["status"] == "PENDING"

@pytest.mark.asyncio
async def test_customer_next_visit_auto_settlement():
    """Customer returns on next visit, pays ₹500, settling the previous ₹200 udhaar and paying ₹300 for new items."""
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as ac:
        # Step 1: Customer takes ₹200 khata
        await ac.post("/api/v1/customer/pay-later", json={
            "merchant_id": "sharma-kirana-001",
            "customer_name": "Rahul Kumar",
            "customer_phone": "+919811229988",
            "amount": 200.0
        })

        # Step 2: Next visit - customer pays ₹500 with auto-settlement enabled
        settle_res = await ac.post("/api/v1/customer/pay-and-settle", json={
            "merchant_id": "sharma-kirana-001",
            "customer_name": "Rahul Kumar",
            "customer_phone": "+919811229988",
            "total_payment": 500.0,
            "settle_khata": True,
            "payment_mode": "Paytm UPI"
        })
    assert settle_res.status_code == 200
    data = settle_res.json()
    assert data["status"] == "SUCCESS"
    assert data["total_payment"] == 500.0
    assert data["khata_settled_amount"] == 200.0
    assert data["net_new_purchase"] == 300.0
    assert data["khata_status"] == "SETTLED"
    assert "Paytm par 500 rupaye prapt hue. Aur purana 200 rupaye udhaar chukta hua!" in data["soundbox_announcement"]

    # Step 3: Verify merchant's khata list shows Rahul's entry marked SETTLED
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as ac:
        khata_res = await ac.get("/api/v1/khata/list?merchant_id=sharma-kirana-001")
    entries = khata_res.json()["entries"]
    rahul_entry = next((e for e in entries if e["customer_name"] == "Rahul Kumar"), None)
    assert rahul_entry["status"] == "SETTLED"
    assert rahul_entry["amount_due"] == 0.0

@pytest.mark.asyncio
async def test_counter_qr_code_image():
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get("/api/v1/merchant/counter-qr?merchant_id=sharma-kirana-001")
    assert res.status_code == 200
    assert res.headers["content-type"] == "image/png"
    assert len(res.content) > 100  # Valid PNG image bytes

@pytest.mark.asyncio
async def test_merchant_live_feed():
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as ac:
        # Trigger a pay-later
        await ac.post("/api/v1/customer/pay-later", json={
            "merchant_id": "sharma-kirana-001",
            "customer_name": "Deepak Verma",
            "customer_phone": "+919800112233",
            "amount": 350.0
        })

        feed_res = await ac.get("/api/v1/merchant/live-feed")
    assert feed_res.status_code == 200
    feed = feed_res.json()
    assert len(feed) >= 1
    latest = feed[0]
    assert latest["customer_name"] == "Deepak Verma"
    assert latest["event_type"] == "KHATA_RECORDED"
    assert latest["total_amount"] == 350.0

@pytest.mark.asyncio
async def test_demo_simulation_endpoints():
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as ac:
        # 1. Simulate QR Udhaar
        sim_res = await ac.post("/api/v1/demo/simulate-qr-udhaar?customer_name=SimulatedUser&amount=450.0")
        assert sim_res.status_code == 201
        assert sim_res.json()["amount"] == 450.0
        assert "SimulatedUser" in sim_res.json()["soundbox_announcement"]

        # 2. Simulate QR Settlement
        settle_res = await ac.post("/api/v1/demo/simulate-qr-settlement?customer_name=SimulatedUser&payment_amount=600.0&settle_amount=450.0")
        assert settle_res.status_code == 200
        assert settle_res.json()["khata_settled_amount"] == 450.0
        assert settle_res.json()["net_new_purchase"] == 150.0

        # 3. Reset demo data
        reset_res = await ac.post("/api/v1/demo/reset")
        assert reset_res.status_code == 200
        assert reset_res.json()["status"] == "SUCCESS"
