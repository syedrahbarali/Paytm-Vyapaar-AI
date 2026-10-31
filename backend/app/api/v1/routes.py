import datetime
import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc

from app.database import get_db, Merchant, Transaction, KhataEntry, LoanApplication
from app.schemas.api_models import (
    DashboardMetricsResponse, MerchantDto, TodaySummaryDto, TransactionDto,
    KhataSummaryDto, LoanOfferDto, KhataListResponse, KhataEntryDto,
    KhataReminderRequest, KhataReminderResponse, LoanClaimRequest, LoanClaimResponse,
    SoundboxWebhookRequest, SoundboxWebhookResponse, UpdatedMetricsDto,
    VoiceQueryResponse, VoiceQueryPayloadDto, DebtorDto, VoiceLoanOfferDto
)
from app.services.voice_service import voice_service
from app.services.whatsapp_service import whatsapp_service
from app.config import settings

router = APIRouter()

# -------------------------------------------------------------
# 1. Dashboard Metrics Endpoint
# -------------------------------------------------------------
@router.get("/dashboard/metrics", response_model=DashboardMetricsResponse)
async def get_dashboard_metrics(merchant_id: str = "sharma-kirana-001", db: AsyncSession = Depends(get_db)):
    merchant = await db.get(Merchant, merchant_id)
    if not merchant:
        raise HTTPException(status_code=404, detail=f"Merchant {merchant_id} not found.")

    # Calculate deterministic total sales & txn count
    sales_query = select(
        func.coalesce(func.sum(Transaction.amount), 0.0),
        func.count(Transaction.id)
    ).where(Transaction.merchant_id == merchant_id)
    sales_res = await db.execute(sales_query)
    total_sales, txn_count = sales_res.one()

    # Recent transactions
    txns_query = select(Transaction).where(Transaction.merchant_id == merchant_id).order_by(desc(Transaction.timestamp)).limit(10)
    txns_res = await db.execute(txns_query)
    transactions = txns_res.scalars().all()

    # Khata totals
    khata_query = select(
        func.coalesce(func.sum(KhataEntry.amount_due), 0.0),
        func.count(KhataEntry.id)
    ).where(KhataEntry.merchant_id == merchant_id, KhataEntry.status != "SETTLED")
    khata_res = await db.execute(khata_query)
    khata_pending, khata_count = khata_res.one()

    crit_query = select(func.count(KhataEntry.id)).where(KhataEntry.merchant_id == merchant_id, KhataEntry.status == "CRITICAL")
    crit_res = await db.execute(crit_query)
    critical_count = crit_res.scalar_one()

    # Loan status
    loan_query = select(LoanApplication).where(LoanApplication.merchant_id == merchant_id).order_by(desc(LoanApplication.id)).limit(1)
    loan_res = await db.execute(loan_query)
    loan = loan_res.scalar_one_or_none()

    return DashboardMetricsResponse(
        merchant=MerchantDto(
            id=merchant.id,
            business_name=merchant.business_name,
            soundbox_device_id=merchant.soundbox_device_id,
            soundbox_online=merchant.soundbox_online,
            health_score=merchant.health_score
        ),
        today_summary=TodaySummaryDto(
            total_sales=float(total_sales),
            transaction_count=int(txn_count),
            peak_hour="6:00 PM - 8:00 PM"
        ),
        recent_transactions=[
            TransactionDto(
                id=t.id,
                payer_name=t.payer_name,
                amount=float(t.amount),
                payment_mode=t.payment_mode,
                timestamp=t.timestamp.isoformat() if t.timestamp else "",
                status=t.status,
                chime_played=t.chime_played
            ) for t in transactions
        ],
        khata_summary=KhataSummaryDto(
            total_pending_amount=float(khata_pending),
            overdue_count=int(khata_count),
            critical_count=int(critical_count)
        ),
        loan_offer=LoanOfferDto(
            eligible=True,
            pre_approved_amount=float(loan.pre_approved_amount) if loan else 50000.00,
            daily_sweep=float(loan.daily_sweep_amount) if loan else 300.00,
            interest_rate=f"{loan.interest_rate_pct if loan else 1.25}% flat",
            tenure_days=int(loan.tenure_days) if loan else 180,
            bank_account_mask=loan.bank_account_mask if loan else "Paytm Payments Bank **********4821"
        )
    )

# -------------------------------------------------------------
# 2. Voice Copilot Query Endpoint
# -------------------------------------------------------------
@router.post("/copilot/voice-query", response_model=VoiceQueryResponse)
async def process_voice_query(
    request: Request,
    merchant_id: str = Form("sharma-kirana-001"),
    audio_file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    merchant = await db.get(Merchant, merchant_id)
    if not merchant:
        raise HTTPException(status_code=404, detail="Merchant not found")

    audio_bytes = await audio_file.read()
    transcription = await voice_service.transcribe_audio(audio_bytes, audio_file.filename or "voice.m4a")

    # Deterministic DB calculation
    sales_res = await db.execute(
        select(func.coalesce(func.sum(Transaction.amount), 0.0), func.count(Transaction.id))
        .where(Transaction.merchant_id == merchant_id)
    )
    total_sales, txn_count = sales_res.one()

    khata_entries_res = await db.execute(
        select(KhataEntry).where(KhataEntry.merchant_id == merchant_id, KhataEntry.status != "SETTLED")
    )
    khata_entries = khata_entries_res.scalars().all()
    total_khata = sum(float(e.amount_due) for e in khata_entries)

    # Intent routing and response text formulation
    intent, reply_text = await voice_service.parse_intent_and_reply(
        transcription, float(total_sales), float(total_khata), len(khata_entries)
    )

    # Speech Synthesis
    audio_rel_url = await voice_service.synthesize_speech(reply_text)
    base_url = str(request.base_url).rstrip("/")
    full_audio_url = f"{base_url}{audio_rel_url}"

    return VoiceQueryResponse(
        status="SUCCESS",
        transcription=transcription,
        intent=intent,
        voice_reply_audio_url=full_audio_url,
        voice_reply_transcript=reply_text,
        data_payload=VoiceQueryPayloadDto(
            today_total_sales=float(total_sales),
            today_txn_count=int(txn_count),
            total_khata_pending=float(total_khata),
            overdue_customers=[
                DebtorDto(
                    khata_id=e.id,
                    name=e.customer_name,
                    phone=e.customer_phone,
                    amount=float(e.amount_due),
                    days_overdue=e.days_overdue,
                    urgency=e.status
                ) for e in khata_entries
            ],
            loan_offer=VoiceLoanOfferDto(
                eligible=True,
                amount=50000.00,
                score=merchant.health_score
            )
        )
    )

# -------------------------------------------------------------
# 3. Khata Ledger & WhatsApp Reminder Endpoints
# -------------------------------------------------------------
@router.get("/khata/list", response_model=KhataListResponse)
async def list_khata_entries(merchant_id: str = "sharma-kirana-001", db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(KhataEntry).where(KhataEntry.merchant_id == merchant_id))
    entries = res.scalars().all()
    total_due = sum(float(e.amount_due) for e in entries if e.status != "SETTLED")

    return KhataListResponse(
        total_outstanding=total_due,
        entries=[
            KhataEntryDto(
                id=e.id,
                customer_name=e.customer_name,
                customer_phone=e.customer_phone,
                amount_due=float(e.amount_due),
                due_date=e.due_date,
                days_overdue=e.days_overdue,
                status=e.status,
                last_reminder_sent=e.last_reminder_sent
            ) for e in entries
        ]
    )

@router.post("/khata/send-reminder", response_model=KhataReminderResponse)
async def send_khata_reminder(req: KhataReminderRequest, db: AsyncSession = Depends(get_db)):
    khata = await db.get(KhataEntry, req.khata_id)
    if not khata:
        raise HTTPException(status_code=404, detail="Khata entry not found")

    dispatch_res = await whatsapp_service.send_khata_collection_link(
        phone=khata.customer_phone,
        customer_name=khata.customer_name,
        amount=float(khata.amount_due),
        khata_id=khata.id
    )

    khata.status = "REMINDED"
    khata.last_reminder_sent = dispatch_res["sent_at"]
    await db.commit()

    return KhataReminderResponse(
        status="DELIVERED",
        khata_id=khata.id,
        recipient=khata.customer_phone,
        customer_name=khata.customer_name,
        payment_link=dispatch_res["payment_link"],
        sent_at=dispatch_res["sent_at"]
    )

# -------------------------------------------------------------
# 4. Lending Claim Endpoint
# -------------------------------------------------------------
@router.post("/loan/claim", response_model=LoanClaimResponse)
async def claim_loan(req: LoanClaimRequest, db: AsyncSession = Depends(get_db)):
    merchant = await db.get(Merchant, req.merchant_id)
    if not merchant:
        raise HTTPException(status_code=404, detail="Merchant not found")

    loan_query = select(LoanApplication).where(LoanApplication.merchant_id == req.merchant_id).limit(1)
    loan_res = await db.execute(loan_query)
    loan = loan_res.scalar_one_or_none()

    now = datetime.datetime.now(datetime.timezone.utc)
    if loan:
        loan.status = "DISBURSED"
        loan.claimed_at = now
        await db.commit()

    disbursal_id = f"LN_PTM_{uuid.uuid4().hex[:8].upper()}"
    return LoanClaimResponse(
        status="DISBURSED",
        disbursal_id=disbursal_id,
        amount=req.amount,
        credited_to=loan.bank_account_mask if loan else "Paytm Payments Bank **********4821",
        daily_sweep_amount=float(loan.daily_sweep_amount) if loan else 300.00,
        disbursed_at=now.isoformat(),
        message="₹50,000 has been credited to your Paytm Payments Bank account. Micro-sweep of ₹300/day activated."
    )

# -------------------------------------------------------------
# 5. Soundbox Payment Webhook (Simulation / Live IoT)
# -------------------------------------------------------------
@router.post("/soundbox/webhook", response_model=SoundboxWebhookResponse, status_code=201)
async def handle_soundbox_webhook(req: SoundboxWebhookRequest, db: AsyncSession = Depends(get_db)):
    # Lookup merchant by soundbox device id
    res = await db.execute(select(Merchant).where(Merchant.soundbox_device_id == req.soundbox_device_id))
    merchant = res.scalar_one_or_none()
    merchant_id = merchant.id if merchant else "sharma-kirana-001"

    # Insert immutable transaction
    txn_id = f"txn_{uuid.uuid4().hex[:8]}"
    new_txn = Transaction(
        id=txn_id,
        merchant_id=merchant_id,
        idempotency_key=req.idempotency_key,
        amount=req.amount,
        payment_mode=req.payment_mode,
        payer_name=req.payer_name,
        status="SUCCESS",
        chime_played=True,
        timestamp=datetime.datetime.now(datetime.timezone.utc)
    )
    db.add(new_txn)
    await db.commit()

    # Recalculate totals
    sales_res = await db.execute(
        select(func.coalesce(func.sum(Transaction.amount), 0.0), func.count(Transaction.id))
        .where(Transaction.merchant_id == merchant_id)
    )
    total_sales, txn_count = sales_res.one()

    return SoundboxWebhookResponse(
        status="SUCCESS",
        transaction_id=txn_id,
        soundbox_chime=f"Paytm par ₹{int(req.amount)} prapt hue",
        updated_metrics=UpdatedMetricsDto(
            today_total_sales=float(total_sales),
            today_txn_count=int(txn_count)
        )
    )
