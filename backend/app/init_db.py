import datetime
import uuid
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import Base, engine, AsyncSessionLocal, Merchant, Transaction, KhataEntry, LoanApplication

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Seed default merchant and demo data if not present
    async with AsyncSessionLocal() as session:
        merchant = await session.get(Merchant, "sharma-kirana-001")
        if not merchant:
            merchant = Merchant(
                id="sharma-kirana-001",
                business_name="Sharma Kirana Store",
                phone_number="+919876500001",
                soundbox_device_id="SB-DELHI-981",
                soundbox_online=True,
                health_score=88,
                created_at=datetime.datetime.now(datetime.timezone.utc)
            )
            session.add(merchant)

            # Khata entries (From Master Spec: Ramesh ₹1,400 & Amit ₹850)
            khata1 = KhataEntry(
                id="khata_001",
                merchant_id="sharma-kirana-001",
                customer_name="Ramesh General Store",
                customer_phone="+919876543210",
                amount_due=1400.00,
                due_date="2026-10-19",
                days_overdue=12,
                status="CRITICAL"
            )
            khata2 = KhataEntry(
                id="khata_002",
                merchant_id="sharma-kirana-001",
                customer_name="Amit Kumar",
                customer_phone="+919811223344",
                amount_due=850.00,
                due_date="2026-10-27",
                days_overdue=4,
                status="PENDING"
            )
            session.add_all([khata1, khata2])

            # Pre-approved Loan
            loan = LoanApplication(
                id="loan_sharma_01",
                merchant_id="sharma-kirana-001",
                pre_approved_amount=50000.00,
                daily_sweep_amount=300.00,
                interest_rate_pct=1.25,
                tenure_days=180,
                bank_account_mask="Paytm Payments Bank **********4821",
                status="OFFERED"
            )
            session.add(loan)

            # Seed base transactions totalling ₹9,420 across 42 txns
            # We add representative recent transactions
            recent_seed = [
                ("txn_101", 150.00, "Aakash Gupta", "Paytm UPI", 5),
                ("txn_100", 420.00, "Rohit Verma", "Paytm QR", 15),
                ("txn_099", 850.00, "Suresh Raina", "Paytm UPI", 30),
                ("txn_098", 200.00, "Pooja Sharma", "Paytm QR", 45),
                ("txn_097", 1200.00, "Deepak Stores", "Paytm UPI", 60),
                ("txn_base", 6600.00, "Earlier Counter Payments (37 Txns)", "Paytm UPI", 180),
            ]
            
            now = datetime.datetime.now(datetime.timezone.utc)
            for tid, amt, name, mode, mins_ago in recent_seed:
                t = Transaction(
                    id=tid,
                    merchant_id="sharma-kirana-001",
                    idempotency_key=f"IDEMP_{tid}",
                    amount=amt,
                    payment_mode=mode,
                    payer_name=name,
                    status="SUCCESS",
                    chime_played=True,
                    timestamp=now - datetime.timedelta(minutes=mins_ago)
                )
                session.add(t)

            await session.commit()
