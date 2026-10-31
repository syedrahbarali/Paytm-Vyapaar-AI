# Paytm VyapaarAI — Android API Contract for Salwa

**Base URL (Local/LAN testing):** `http://<SERVER_IP>:8000`  
**API Prefix:** `/api/v1`

---

## 1. Dashboard Metrics & Feed
Load on app launch and pull-to-refresh on Screen 1 (Home Dashboard).

- **Method & Route:** `GET /api/v1/dashboard/metrics?merchant_id={merchant_id}`
- **Sample Request:** `GET /api/v1/dashboard/metrics?merchant_id=sharma-kirana-001`
- **Response `200 OK`:**
```json
{
  "merchant": {
    "id": "sharma-kirana-001",
    "business_name": "Sharma Kirana Store",
    "soundbox_device_id": "SB-DELHI-981",
    "soundbox_online": true,
    "health_score": 88
  },
  "today_summary": {
    "total_sales": 9420.00,
    "transaction_count": 42,
    "peak_hour": "6:00 PM - 8:00 PM"
  },
  "recent_transactions": [
    {
      "id": "txn_101",
      "payer_name": "Aakash Gupta",
      "amount": 150.00,
      "payment_mode": "Paytm UPI",
      "timestamp": "2026-10-31T11:20:10Z",
      "status": "SUCCESS",
      "chime_played": true
    },
    {
      "id": "txn_100",
      "payer_name": "Rohit Verma",
      "amount": 420.00,
      "payment_mode": "Paytm QR",
      "timestamp": "2026-10-31T11:05:00Z",
      "status": "SUCCESS",
      "chime_played": true
    }
  ],
  "khata_summary": {
    "total_pending_amount": 2250.00,
    "overdue_count": 2,
    "critical_count": 1
  },
  "loan_offer": {
    "eligible": true,
    "pre_approved_amount": 50000.00,
    "daily_sweep": 300.00,
    "interest_rate": "1.25% flat",
    "tenure_days": 180,
    "bank_account_mask": "Paytm Payments Bank **********4821"
  }
}
```

---

## 2. Voice Copilot Query (Push-to-Talk)
Used by the Centered Floating Mic FAB on Screen 1 & Screen 2 (Voice Copilot Modal Overlay).

- **Method & Route:** `POST /api/v1/copilot/voice-query`
- **Content-Type:** `multipart/form-data`
- **Request Parameters:**
  - `merchant_id` (Text / Form field): e.g. `"sharma-kirana-001"`
  - `audio_file` (Binary File): Recorded `.m4a` or `.wav` from Android `MediaRecorder`
- **Response `200 OK`:**
```json
{
  "status": "SUCCESS",
  "transcription": "Bhaiya aaj kitna bika aur udhari kiski baaki hai?",
  "intent": "DAILY_SUMMARY_AND_KHATA",
  "voice_reply_audio_url": "http://<SERVER_IP>:8000/static/audio/reply_9821.mp3",
  "voice_reply_transcript": "Sharma ji, aaj total ₹9,420 ki sale hui hai aur 2 customers ka ₹2,250 udhaar baaki hai.",
  "data_payload": {
    "today_total_sales": 9420.00,
    "today_txn_count": 42,
    "total_khata_pending": 2250.00,
    "overdue_customers": [
      {
        "khata_id": "khata_001",
        "name": "Ramesh General Store",
        "phone": "+919876543210",
        "amount": 1400.00,
        "days_overdue": 12,
        "urgency": "CRITICAL"
      },
      {
        "khata_id": "khata_002",
        "name": "Amit Kumar",
        "phone": "+919811223344",
        "amount": 850.00,
        "days_overdue": 4,
        "urgency": "PENDING"
      }
    ],
    "loan_offer": {
      "eligible": true,
      "amount": 50000.00,
      "score": 88
    }
  }
}
```

---

## 3. Khata Recovery Directory & 1-Click WhatsApp Trigger
Used by Screen 3 (Khata Udhaar Recovery Directory) & the Dashboard Khata Alert card.

### A. Get All Khata Entries
- **Method & Route:** `GET /api/v1/khata/list?merchant_id={merchant_id}`
- **Response `200 OK`:**
```json
{
  "total_outstanding": 2250.00,
  "entries": [
    {
      "id": "khata_001",
      "customer_name": "Ramesh General Store",
      "customer_phone": "+919876543210",
      "amount_due": 1400.00,
      "due_date": "2026-10-19",
      "days_overdue": 12,
      "status": "CRITICAL",
      "last_reminder_sent": null
    },
    {
      "id": "khata_002",
      "customer_name": "Amit Kumar",
      "customer_phone": "+919811223344",
      "amount_due": 850.00,
      "due_date": "2026-10-27",
      "days_overdue": 4,
      "status": "PENDING",
      "last_reminder_sent": null
    }
  ]
}
```

### B. Trigger WhatsApp Reminder
- **Method & Route:** `POST /api/v1/khata/send-reminder`
- **Content-Type:** `application/json`
- **Payload:**
```json
{
  "khata_id": "khata_001"
}
```
- **Response `200 OK`:**
```json
{
  "status": "DELIVERED",
  "khata_id": "khata_001",
  "recipient": "+919876543210",
  "customer_name": "Ramesh General Store",
  "payment_link": "https://p.paytm.me/qr/pay?amt=1400.00&ref=KHATA_001",
  "sent_at": "2026-10-31T11:30:00Z"
}
```

---

## 4. 1-Click Paytm Lending Claim Screen
Used by Screen 4 (1-Click Paytm Lending Claim Modal).

- **Method & Route:** `POST /api/v1/loan/claim`
- **Content-Type:** `application/json`
- **Payload:**
```json
{
  "merchant_id": "sharma-kirana-001",
  "amount": 50000.00,
  "otp_consent": "849201"
}
```
- **Response `200 OK`:**
```json
{
  "status": "DISBURSED",
  "disbursal_id": "LN_PTM_88192839",
  "amount": 50000.00,
  "credited_to": "Paytm Payments Bank **********4821",
  "daily_sweep_amount": 300.00,
  "disbursed_at": "2026-10-31T11:32:00Z",
  "message": "₹50,000 has been credited to your Paytm Payments Bank account. Micro-sweep of ₹300/day activated."
}
```

---

## 5. Simulated Counter Payment (For Hackathon Demos)
Can be triggered from an admin view, mock button, or demo script to simulate a customer QR scan.

- **Method & Route:** `POST /api/v1/soundbox/webhook`
- **Content-Type:** `application/json`
- **Payload:**
```json
{
  "soundbox_device_id": "SB-DELHI-981",
  "idempotency_key": "TXN_UPI_982194821",
  "amount": 150.00,
  "payer_name": "Aakash Gupta",
  "payment_mode": "UPI",
  "timestamp": "2026-10-31T11:33:00Z"
}
```
- **Response `201 Created`:**
```json
{
  "status": "SUCCESS",
  "transaction_id": "txn_101",
  "soundbox_chime": "Paytm par ₹150 prapt hue",
  "updated_metrics": {
    "today_total_sales": 9570.00,
    "today_txn_count": 43
  }
}
```

---

## 6. Ready-to-Copy Kotlin Retrofit Interface & Models for Salwa

```kotlin
import okhttp3.MultipartBody
import okhttp3.RequestBody
import retrofit2.Response
import retrofit2.http.*

interface VyapaarApiService {

    @GET("api/v1/dashboard/metrics")
    suspend fun getDashboardMetrics(
        @Query("merchant_id") merchantId: String
    ): Response<DashboardMetricsResponse>

    @Multipart
    @POST("api/v1/copilot/voice-query")
    suspend fun sendVoiceQuery(
        @Part("merchant_id") merchantId: RequestBody,
        @Part audioFile: MultipartBody.Part
    ): Response<VoiceQueryResponse>

    @GET("api/v1/khata/list")
    suspend fun getKhataList(
        @Query("merchant_id") merchantId: String
    ): Response<KhataListResponse>

    @POST("api/v1/khata/send-reminder")
    suspend fun triggerKhataReminder(
        @Body request: KhataReminderRequest
    ): Response<KhataReminderResponse>

    @POST("api/v1/loan/claim")
    suspend fun claimLoanAdvance(
        @Body request: LoanClaimRequest
    ): Response<LoanClaimResponse>

    @POST("api/v1/soundbox/webhook")
    suspend fun simulateSoundboxPayment(
        @Body request: SoundboxWebhookRequest
    ): Response<SoundboxWebhookResponse>
}

// Data Transfer Objects (DTOs)
data class DashboardMetricsResponse(
    val merchant: MerchantDto,
    val today_summary: TodaySummaryDto,
    val recent_transactions: List<TransactionDto>,
    val khata_summary: KhataSummaryDto,
    val loan_offer: LoanOfferDto
)

data class MerchantDto(
    val id: String,
    val business_name: String,
    val soundbox_device_id: String,
    val soundbox_online: Boolean,
    val health_score: Int
)

data class TodaySummaryDto(
    val total_sales: Double,
    val transaction_count: Int,
    val peak_hour: String
)

data class TransactionDto(
    val id: String,
    val payer_name: String,
    val amount: Double,
    val payment_mode: String,
    val timestamp: String,
    val status: String,
    val chime_played: Boolean
)

data class KhataSummaryDto(
    val total_pending_amount: Double,
    val overdue_count: Int,
    val critical_count: Int
)

data class LoanOfferDto(
    val eligible: Boolean,
    val pre_approved_amount: Double,
    val daily_sweep: Double,
    val interest_rate: String,
    val tenure_days: Int,
    val bank_account_mask: String
)

data class VoiceQueryResponse(
    val status: String,
    val transcription: String,
    val intent: String,
    val voice_reply_audio_url: String,
    val voice_reply_transcript: String,
    val data_payload: VoiceQueryPayloadDto
)

data class VoiceQueryPayloadDto(
    val today_total_sales: Double,
    val today_txn_count: Int,
    val total_khata_pending: Double,
    val overdue_customers: List<DebtorDto>,
    val loan_offer: VoiceLoanOfferDto
)

data class DebtorDto(
    val khata_id: String,
    val name: String,
    val phone: String,
    val amount: Double,
    val days_overdue: Int,
    val urgency: String
)

data class VoiceLoanOfferDto(
    val eligible: Boolean,
    val amount: Double,
    val score: Int
)

data class KhataListResponse(
    val total_outstanding: Double,
    val entries: List<KhataEntryDto>
)

data class KhataEntryDto(
    val id: String,
    val customer_name: String,
    val customer_phone: String,
    val amount_due: Double,
    val due_date: String,
    val days_overdue: Int,
    val status: String,
    val last_reminder_sent: String?
)

data class KhataReminderRequest(val khata_id: String)
data class KhataReminderResponse(
    val status: String,
    val khata_id: String,
    val recipient: String,
    val customer_name: String,
    val payment_link: String,
    val sent_at: String
)

data class LoanClaimRequest(
    val merchant_id: String,
    val amount: Double,
    val otp_consent: String
)

data class LoanClaimResponse(
    val status: String,
    val disbursal_id: String,
    val amount: Double,
    val credited_to: String,
    val daily_sweep_amount: Double,
    val disbursed_at: String,
    val message: String
)

data class SoundboxWebhookRequest(
    val soundbox_device_id: String,
    val idempotency_key: String,
    val amount: Double,
    val payer_name: String,
    val payment_mode: String,
    val timestamp: String
)

data class SoundboxWebhookResponse(
    val status: String,
    val transaction_id: String,
    val soundbox_chime: String,
    val updated_metrics: UpdatedMetricsDto
)

data class UpdatedMetricsDto(
    val today_total_sales: Double,
    val today_txn_count: Int
)
```
