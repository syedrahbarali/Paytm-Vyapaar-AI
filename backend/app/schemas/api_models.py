from pydantic import BaseModel, Field
from typing import List, Optional
import datetime

# --- Dashboard Schemas ---
class MerchantDto(BaseModel):
    id: str
    business_name: str
    soundbox_device_id: str
    soundbox_online: bool
    health_score: int

class TodaySummaryDto(BaseModel):
    total_sales: float
    transaction_count: int
    peak_hour: str

class TransactionDto(BaseModel):
    id: str
    payer_name: str
    amount: float
    payment_mode: str
    timestamp: str
    status: str
    chime_played: bool

class KhataSummaryDto(BaseModel):
    total_pending_amount: float
    overdue_count: int
    critical_count: int

class LoanOfferDto(BaseModel):
    eligible: bool
    pre_approved_amount: float
    daily_sweep: float
    interest_rate: str
    tenure_days: int
    bank_account_mask: str

class DashboardMetricsResponse(BaseModel):
    merchant: MerchantDto
    today_summary: TodaySummaryDto
    recent_transactions: List[TransactionDto]
    khata_summary: KhataSummaryDto
    loan_offer: LoanOfferDto

# --- Khata Schemas ---
class KhataEntryDto(BaseModel):
    id: str
    customer_name: str
    customer_phone: str
    amount_due: float
    due_date: str
    days_overdue: int
    status: str
    last_reminder_sent: Optional[str] = None

class KhataListResponse(BaseModel):
    total_outstanding: float
    entries: List[KhataEntryDto]

class KhataReminderRequest(BaseModel):
    khata_id: str

class KhataReminderResponse(BaseModel):
    status: str
    khata_id: str
    recipient: str
    customer_name: str
    payment_link: str
    sent_at: str

# --- Loan Schemas ---
class LoanClaimRequest(BaseModel):
    merchant_id: str
    amount: float
    otp_consent: str

class LoanClaimResponse(BaseModel):
    status: str
    disbursal_id: str
    amount: float
    credited_to: str
    daily_sweep_amount: float
    disbursed_at: str
    message: str

# --- Soundbox Webhook Schemas ---
class SoundboxWebhookRequest(BaseModel):
    soundbox_device_id: str
    idempotency_key: str
    amount: float
    payer_name: str
    payment_mode: str = "Paytm UPI"
    timestamp: Optional[str] = None

class UpdatedMetricsDto(BaseModel):
    today_total_sales: float
    today_txn_count: int

class SoundboxWebhookResponse(BaseModel):
    status: str
    transaction_id: str
    soundbox_chime: str
    updated_metrics: UpdatedMetricsDto

# --- Voice Query Schemas ---
class DebtorDto(BaseModel):
    khata_id: str
    name: str
    phone: str
    amount: float
    days_overdue: int
    urgency: str

class VoiceLoanOfferDto(BaseModel):
    eligible: bool
    amount: float
    score: int

class VoiceQueryPayloadDto(BaseModel):
    today_total_sales: float
    today_txn_count: int
    total_khata_pending: float
    overdue_customers: List[DebtorDto]
    loan_offer: VoiceLoanOfferDto

class VoiceQueryResponse(BaseModel):
    status: str
    transcription: str
    intent: str
    voice_reply_audio_url: str
    voice_reply_transcript: str
    data_payload: VoiceQueryPayloadDto
