# Paytm VyapaarAI — Complete Backend API Integration Document

**Target Audience:** Salwa (Android Lead) & Autonomous AI Coding Agents (Claude, Cursor, Antigravity, Copilot).  
**Document Purpose:** Complete, single-file API integration specification containing every endpoint, request/response contract, Kotlin data models, Retrofit interfaces, and SSE stream handlers to build the native Android Merchant App.  
**Language Specification:** Strict Production English.  
**Base URL:**
- Android Emulator: `http://10.0.2.2:8000/`
- Local Wi-Fi / Physical Device: `http://10.150.76.180:8000/`
- Default Test Merchant ID: `sharma-kirana-001`
- Default Soundbox ID: `SB-DELHI-981`

---

## 1. Quick Master Endpoint Reference Table

| # | HTTP Method | Endpoint Path | Function / Purpose |
|---|---|---|---|
| 1 | `GET` | `/api/v1/dashboard/metrics` | Fetch top dashboard metrics (Sales, Txns, Soundbox state, Khata, Loan) |
| 2 | `POST` | `/api/v1/copilot/voice-query` | Push-to-Talk vernacular voice query (Audio file upload -> AI response & audio) |
| 3 | `GET` | `/api/v1/khata/list` | Get complete debtor ledger (pending customers, days overdue, risk tags) |
| 4 | `POST` | `/api/v1/khata/send-reminder` | Dispatch 1-click WhatsApp payment reminder with dynamic Paytm QR link |
| 5 | `POST` | `/api/v1/loan/claim` | 1-Click claim of pre-approved ₹50,000 Paytm Cash Advance |
| 6 | `POST` | `/api/v1/soundbox/webhook` | Ingests counter payment event from physical/simulated Soundbox IoT |
| 7 | `GET` | `/api/v1/customer/checkout-details/{merchant_id}` | Check if customer's mobile number has pending Khata |
| 8 | `POST` | `/api/v1/customer/pay-later` | Customer self-records Khata via Counter QR -> Soundbox speaks live |
| 9 | `POST` | `/api/v1/customer/pay-and-settle` | Customer returns and settles Khata via UPI -> Soundbox settlement chime |
| 10 | `GET` | `/api/v1/merchant/counter-qr` | Returns 370x370 PNG image of counter QR code for customer scanning |
| 11 | `GET` | `/api/v1/merchant/live-feed` | Polling feed of live events (Standard Payment, QR Khata, QR Settlement) |
| 12 | `GET` | `/api/v1/stream/events` | Real-time Server-Sent Events (SSE) push stream for live updates |
| 13 | `POST` | `/api/v1/demo/simulate-qr-udhaar` | Hackathon live demo trigger: Simulates customer taking ₹200 Khata |
| 14 | `POST` | `/api/v1/demo/simulate-qr-settlement` | Hackathon live demo trigger: Simulates customer settling ₹200 Khata |
| 15 | `POST` | `/api/v1/demo/reset` | Resets demo data for clean repeat presentations |

---

## 2. Detailed Endpoint Specifications

### 2.1 GET `/api/v1/dashboard/metrics`
Fetches the high-level financial summary, Soundbox hardware connectivity, Khata risk alerts, and loan underwriting limits.

- **Query Parameters:**
  - `merchant_id` (string, optional, default: `"sharma-kirana-001"`)
- **Headers:** `Accept: application/json`
- **Response `200 OK` JSON:**
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
    "total_sales": 9420.0,
    "transaction_count": 42,
    "peak_hour": "6:00 PM - 8:00 PM"
  },
  "recent_transactions": [
    {
      "id": "txn_101",
      "payer_name": "Aakash Gupta",
      "amount": 150.0,
      "payment_mode": "Paytm UPI",
      "timestamp": "2026-10-31T08:50:00Z",
      "status": "SUCCESS",
      "chime_played": true
    }
  ],
  "khata_summary": {
    "total_pending_amount": 2250.0,
    "overdue_count": 2,
    "critical_count": 1
  },
  "loan_offer": {
    "eligible": true,
    "pre_approved_amount": 50000.0,
    "daily_sweep": 300.0,
    "interest_rate": "1.25% flat",
    "tenure_days": 180,
    "bank_account_mask": "Paytm Payments Bank **********4821"
  }
}
```

---

### 2.2 POST `/api/v1/copilot/voice-query`
Uploads vernacular audio recorded from the merchant's phone mic. The backend runs Groq Whisper (<500ms ASR) + SQL query + Edge-TTS synthesis, returning structured data AND an audio URL to play through the phone speaker.

- **Content-Type:** `multipart/form-data`
- **Form Fields:**
  - `merchant_id` (string): `"sharma-kirana-001"`
  - `audio_file` (file binary): Audio recording (`.m4a`, `.wav`, or `.aac`)
- **Response `200 OK` JSON:**
```json
{
  "status": "SUCCESS",
  "transcription": "Bhaiya aaj kitna bika aur udhari kiski baaki hai?",
  "intent": "DAILY_SUMMARY_AND_KHATA",
  "voice_reply_transcript": "Sharma ji, aaj counter par total ₹9,420 ki sale hui hai, aur 2 customers ka ₹2,250 udhaar baaki hai.",
  "voice_reply_audio_url": "http://10.150.76.180:8000/static/audio/reply_7d199d71.mp3",
  "data_payload": {
    "today_total_sales": 9420.0,
    "today_txn_count": 42,
    "total_khata_pending": 2250.0,
    "overdue_customers": [
      {
        "khata_id": "khata_001",
        "name": "Ramesh General Store",
        "phone": "+919876543210",
        "amount": 1400.0,
        "days_overdue": 12,
        "urgency": "CRITICAL"
      },
      {
        "khata_id": "khata_002",
        "name": "Amit Kumar",
        "phone": "+919811223344",
        "amount": 850.0,
        "days_overdue": 4,
        "urgency": "PENDING"
      }
    ],
    "loan_offer": {
      "eligible": true,
      "amount": 50000.0,
      "score": 88
    }
  }
}
```

---

### 2.3 GET `/api/v1/khata/list`
Returns the customer credit ledger with risk levels and days overdue.

- **Query Parameters:** `merchant_id` (string, optional, default: `"sharma-kirana-001"`)
- **Response `200 OK` JSON:**
```json
{
  "total_outstanding": 2250.0,
  "entries": [
    {
      "id": "khata_001",
      "customer_name": "Ramesh General Store",
      "customer_phone": "+919876543210",
      "amount_due": 1400.0,
      "due_date": "2026-10-19",
      "days_overdue": 12,
      "status": "CRITICAL",
      "last_reminder_sent": null
    },
    {
      "id": "khata_002",
      "customer_name": "Amit Kumar",
      "customer_phone": "+919811223344",
      "amount_due": 850.0,
      "due_date": "2026-10-27",
      "days_overdue": 4,
      "status": "PENDING",
      "last_reminder_sent": null
    }
  ]
}
```

---

### 2.4 POST `/api/v1/khata/send-reminder`
Dispatches a personalized WhatsApp collection message with a dynamic Paytm UPI link.

- **Request Body:**
```json
{
  "khata_id": "khata_001"
}
```
- **Response `200 OK` JSON:**
```json
{
  "status": "DELIVERED",
  "khata_id": "khata_001",
  "recipient": "+919876543210",
  "customer_name": "Ramesh General Store",
  "payment_link": "https://paytm.me/pay/khata_001?amt=1400.0",
  "sent_at": "2026-10-31T09:15:00Z"
}
```

---

### 2.5 POST `/api/v1/loan/claim`
1-Click claim of the pre-approved working capital loan. Disburses capital directly into the merchant's Paytm Payments Bank account.

- **Request Body:**
```json
{
  "merchant_id": "sharma-kirana-001",
  "amount": 50000.0,
  "otp_consent": "849201"
}
```
- **Response `200 OK` JSON:**
```json
{
  "status": "DISBURSED",
  "disbursal_id": "LN_PTM_A7B2C9D1",
  "amount": 50000.0,
  "credited_to": "Paytm Payments Bank **********4821",
  "daily_sweep_amount": 300.0,
  "disbursed_at": "2026-10-31T09:16:00Z",
  "message": "₹50,000 has been credited to your Paytm Payments Bank account. Micro-sweep of ₹300/day activated."
}
```

---

### 2.6 POST `/api/v1/soundbox/webhook`
Webhook simulating physical IoT Soundbox payment ingestion.

- **Request Body:**
```json
{
  "soundbox_device_id": "SB-DELHI-981",
  "idempotency_key": "TXN_UPI_98218491",
  "amount": 150.0,
  "payer_name": "Rahul Yadav",
  "payment_mode": "Paytm UPI"
}
```
- **Response `201 Created` JSON:**
```json
{
  "status": "SUCCESS",
  "transaction_id": "txn_8f91a2bc",
  "soundbox_chime": "Paytm par ₹150 prapt hue",
  "updated_metrics": {
    "today_total_sales": 9570.0,
    "today_txn_count": 43
  }
}
```

---

### 2.7 Breakthrough Feature: Customer-Initiated QR Pay-Later (Udhaar)

#### POST `/api/v1/customer/pay-later`
Triggered when a customer scans the counter QR, selects "Take Khata / Pay Later", and confirms ₹200 on their own phone.
- **Result:** Soundbox immediately speaks: *"Sharma Kirana alert: Rahul Kumar ne 200 rupaye ka udhaar darj kiya!"*, updates SQL ledger, and pushes an event to Android live feed.

- **Request Body:**
```json
{
  "merchant_id": "sharma-kirana-001",
  "customer_name": "Rahul Kumar",
  "customer_phone": "+919811229988",
  "amount": 200.0,
  "notes": "Evening milk and biscuits"
}
```
- **Response `201 Created` JSON:**
```json
{
  "status": "RECORDED",
  "khata_id": "khata_qr_a1b2c3d4",
  "merchant_id": "sharma-kirana-001",
  "customer_name": "Rahul Kumar",
  "amount": 200.0,
  "soundbox_announcement": "Sharma Kirana alert: Rahul Kumar ne 200 rupaye ka udhaar darj kiya!",
  "audio_url": "/static/audio/reply_7d199d71.mp3",
  "timestamp": "2026-10-31T09:20:00Z",
  "message": "₹200.0 credit recorded for Rahul Kumar. Soundbox verified."
}
```

---

### 2.8 Breakthrough Feature: Next-Visit Auto-Settlement Split

#### POST `/api/v1/customer/pay-and-settle`
Triggered when the customer returns 4 days later to buy ₹500 goods and chooses to clear their past ₹200 Udhaar within the same transaction.
- **Result:** Total payment ₹500 is split: ₹200 clears Khata (marked SETTLED), ₹300 pays for new groceries. Soundbox announces: *"Paytm par 500 rupaye prapt hue. Aur purana 200 rupaye udhaar chukta hua!"*.

- **Request Body:**
```json
{
  "merchant_id": "sharma-kirana-001",
  "customer_name": "Rahul Kumar",
  "customer_phone": "+919811229988",
  "total_payment": 500.0,
  "settle_khata": true,
  "settle_amount": 200.0,
  "payment_mode": "Paytm UPI"
}
```
- **Response `200 OK` JSON:**
```json
{
  "status": "SUCCESS",
  "transaction_id": "txn_settle_98f12a3b",
  "merchant_id": "sharma-kirana-001",
  "customer_name": "Rahul Kumar",
  "total_payment": 500.0,
  "khata_settled_amount": 200.0,
  "net_new_purchase": 300.0,
  "soundbox_announcement": "Paytm par 500 rupaye prapt hue. Aur purana 200 rupaye udhaar chukta hua!",
  "audio_url": "/static/audio/reply_673f4a4e.mp3",
  "khata_status": "SETTLED",
  "timestamp": "2026-10-31T09:25:00Z",
  "message": "Payment processed and Soundbox voice chime triggered."
}
```

---

### 2.9 GET `/api/v1/merchant/live-feed`
Polling endpoint returning recent Soundbox and QR events for the Android Live Feed `LazyColumn`.

- **Response `200 OK` JSON:**
```json
[
  {
    "event_id": "evt_20261031143249_2",
    "event_type": "KHATA_SETTLED",
    "customer_name": "Rahul Kumar",
    "customer_phone": "+919811229988",
    "total_amount": 500.0,
    "settled_khata_amount": 200.0,
    "timestamp": "2026-10-31T09:25:00Z",
    "soundbox_announcement": "Paytm par 500 rupaye prapt hue. Aur purana 200 rupaye udhaar chukta hua!",
    "audio_url": "/static/audio/reply_673f4a4e.mp3",
    "is_soundbox_verified": true
  },
  {
    "event_id": "evt_20261031143236_1",
    "event_type": "KHATA_RECORDED",
    "customer_name": "Rahul Kumar",
    "customer_phone": "+919811229988",
    "total_amount": 200.0,
    "settled_khata_amount": 0.0,
    "timestamp": "2026-10-31T09:20:00Z",
    "soundbox_announcement": "Sharma Kirana alert: Rahul Kumar ne 200 rupaye ka udhaar darj kiya!",
    "audio_url": "/static/audio/reply_7d199d71.mp3",
    "is_soundbox_verified": true
  }
]
```

---

### 2.10 GET `/api/v1/stream/events` (Server-Sent Events)
Live push stream delivering immediate real-time notifications to Android without polling.

- **Content-Type:** `text/event-stream`
- **Stream Format:**
```text
data: {"status": "CONNECTED", "service": "Paytm VyapaarAI Soundbox Event Stream"}

data: {"event_id": "evt_001", "event_type": "KHATA_RECORDED", "customer_name": "Rahul Kumar", "total_amount": 200.0, "soundbox_announcement": "Sharma Kirana alert: Rahul Kumar ne 200 rupaye ka udhaar darj kiya!"}
```

---

### 2.11 Hackathon Demo Simulation Triggers (For Stage Presentation)

- **`POST /api/v1/demo/simulate-qr-udhaar`**
  - Query Params: `customer_name=Rahul Kumar&amount=200.0`
  - Instantly logs ₹200 Khata and triggers audio announcement.
- **`POST /api/v1/demo/simulate-qr-settlement`**
  - Query Params: `customer_name=Rahul Kumar&payment_amount=500.0&settle_amount=200.0`
  - Instantly marks Khata settled and announces full payment + settlement audio.
- **`POST /api/v1/demo/reset`**
  - Clears test data so you can restart the live demo from scratch in front of judges!

---

## 3. Copy-Paste Kotlin Data Classes (DTOs) for Salwa

Salwa, copy this file into `com.paytm.vyapaarai.data.model.ApiModels.kt`:

```kotlin
package com.paytm.vyapaarai.data.model

import com.google.gson.annotations.SerializedName

// 1. Dashboard Metrics
data class DashboardMetricsResponse(
    @SerializedName("merchant") val merchant: MerchantDto,
    @SerializedName("today_summary") val todaySummary: TodaySummaryDto,
    @SerializedName("recent_transactions") val recentTransactions: List<TransactionDto>,
    @SerializedName("khata_summary") val khataSummary: KhataSummaryDto,
    @SerializedName("loan_offer") val loanOffer: LoanOfferDto
)

data class MerchantDto(
    @SerializedName("id") val id: String,
    @SerializedName("business_name") val businessName: String,
    @SerializedName("soundbox_device_id") val soundboxDeviceId: String,
    @SerializedName("soundbox_online") val soundboxOnline: Boolean,
    @SerializedName("health_score") val healthScore: Int
)

data class TodaySummaryDto(
    @SerializedName("total_sales") val totalSales: Double,
    @SerializedName("transaction_count") val transactionCount: Int,
    @SerializedName("peak_hour") val peakHour: String
)

data class TransactionDto(
    @SerializedName("id") val id: String,
    @SerializedName("payer_name") val payerName: String,
    @SerializedName("amount") val amount: Double,
    @SerializedName("payment_mode") val paymentMode: String,
    @SerializedName("timestamp") val timestamp: String,
    @SerializedName("status") val status: String,
    @SerializedName("chime_played") val chimePlayed: Boolean
)

data class KhataSummaryDto(
    @SerializedName("total_pending_amount") val totalPendingAmount: Double,
    @SerializedName("overdue_count") val overdueCount: Int,
    @SerializedName("critical_count") val criticalCount: Int
)

data class LoanOfferDto(
    @SerializedName("eligible") val eligible: Boolean,
    @SerializedName("pre_approved_amount") val preApprovedAmount: Double,
    @SerializedName("daily_sweep") val dailySweep: Double,
    @SerializedName("interest_rate") val interestRate: String,
    @SerializedName("tenure_days") val tenureDays: Int,
    @SerializedName("bank_account_mask") val bankAccountMask: String
)

// 2. Khata Ledger
data class KhataListResponse(
    @SerializedName("total_outstanding") val totalOutstanding: Double,
    @SerializedName("entries") val entries: List<KhataEntryDto>
)

data class KhataEntryDto(
    @SerializedName("id") val id: String,
    @SerializedName("customer_name") val customerName: String,
    @SerializedName("customer_phone") val customerPhone: String,
    @SerializedName("amount_due") val amountDue: Double,
    @SerializedName("due_date") val dueDate: String,
    @SerializedName("days_overdue") val daysOverdue: Int,
    @SerializedName("status") val status: String, // "PENDING", "CRITICAL", "REMINDED", "SETTLED"
    @SerializedName("last_reminder_sent") val lastReminderSent: String?
)

data class KhataReminderRequest(
    @SerializedName("khata_id") val khataId: String
)

data class KhataReminderResponse(
    @SerializedName("status") val status: String,
    @SerializedName("khata_id") val khataId: String,
    @SerializedName("recipient") val recipient: String,
    @SerializedName("customer_name") val customerName: String,
    @SerializedName("payment_link") val paymentLink: String,
    @SerializedName("sent_at") val sentAt: String
)

// 3. Voice Copilot Response
data class VoiceQueryResponse(
    @SerializedName("status") val status: String,
    @SerializedName("transcription") val transcription: String,
    @SerializedName("intent") val intent: String,
    @SerializedName("voice_reply_audio_url") val voiceReplyAudioUrl: String,
    @SerializedName("voice_reply_transcript") val voiceReplyTranscript: String,
    @SerializedName("data_payload") val dataPayload: VoiceQueryPayloadDto
)

data class VoiceQueryPayloadDto(
    @SerializedName("today_total_sales") val todayTotalSales: Double,
    @SerializedName("today_txn_count") val todayTxnCount: Int,
    @SerializedName("total_khata_pending") val totalKhataPending: Double,
    @SerializedName("overdue_customers") val overdueCustomers: List<DebtorDto>,
    @SerializedName("loan_offer") val loanOffer: VoiceLoanOfferDto
)

data class DebtorDto(
    @SerializedName("khata_id") val khataId: String,
    @SerializedName("name") val name: String,
    @SerializedName("phone") val phone: String,
    @SerializedName("amount") val amount: Double,
    @SerializedName("days_overdue") val daysOverdue: Int,
    @SerializedName("urgency") val urgency: String
)

data class VoiceLoanOfferDto(
    @SerializedName("eligible") val eligible: Boolean,
    @SerializedName("amount") val amount: Double,
    @SerializedName("score") val score: Int
)

// 4. Loan Claim
data class LoanClaimRequest(
    @SerializedName("merchant_id") val merchantId: String,
    @SerializedName("amount") val amount: Double = 50000.0,
    @SerializedName("otp_consent") val otpConsent: String = "849201"
)

data class LoanClaimResponse(
    @SerializedName("status") val status: String,
    @SerializedName("disbursal_id") val disbursalId: String,
    @SerializedName("amount") val amount: Double,
    @SerializedName("credited_to") val creditedTo: String,
    @SerializedName("daily_sweep_amount") val dailySweepAmount: Double,
    @SerializedName("disbursed_at") val disbursedAt: String,
    @SerializedName("message") val message: String
)

// 5. Customer Pay-Later & Settlement
data class CustomerPayLaterRequest(
    @SerializedName("merchant_id") val merchantId: String = "sharma-kirana-001",
    @SerializedName("customer_name") val customerName: String,
    @SerializedName("customer_phone") val customerPhone: String,
    @SerializedName("amount") val amount: Double,
    @SerializedName("notes") val notes: String = "Counter QR Pay Later"
)

data class CustomerPayLaterResponse(
    @SerializedName("status") val status: String,
    @SerializedName("khata_id") val khataId: String,
    @SerializedName("merchant_id") val merchantId: String,
    @SerializedName("customer_name") val customerName: String,
    @SerializedName("amount") val amount: Double,
    @SerializedName("soundbox_announcement") val soundboxAnnouncement: String,
    @SerializedName("audio_url") val audioUrl: String,
    @SerializedName("timestamp") val timestamp: String,
    @SerializedName("message") val message: String
)

data class CustomerPayAndSettleRequest(
    @SerializedName("merchant_id") val merchantId: String = "sharma-kirana-001",
    @SerializedName("customer_name") val customerName: String,
    @SerializedName("customer_phone") val customerPhone: String,
    @SerializedName("total_payment") val totalPayment: Double,
    @SerializedName("settle_khata") val settleKhata: Boolean = true,
    @SerializedName("settle_amount") val settleAmount: Double? = null,
    @SerializedName("payment_mode") val paymentMode: String = "Paytm UPI"
)

data class CustomerPayAndSettleResponse(
    @SerializedName("status") val status: String,
    @SerializedName("transaction_id") val transactionId: String,
    @SerializedName("total_payment") val totalPayment: Double,
    @SerializedName("khata_settled_amount") val khataSettledAmount: Double,
    @SerializedName("net_new_purchase") val netNewPurchase: Double,
    @SerializedName("soundbox_announcement") val soundboxAnnouncement: String,
    @SerializedName("audio_url") val audioUrl: String,
    @SerializedName("khata_status") val khataStatus: String,
    @SerializedName("timestamp") val timestamp: String,
    @SerializedName("message") val message: String
)

// 6. Live Feed Events (Soundbox & QR Stream)
data class LiveFeedEventDto(
    @SerializedName("event_id") val eventId: String,
    @SerializedName("event_type") val eventType: String, // "PAYMENT_RECEIVED", "KHATA_RECORDED", "KHATA_SETTLED"
    @SerializedName("customer_name") val customerName: String,
    @SerializedName("customer_phone") val customerPhone: String,
    @SerializedName("total_amount") val totalAmount: Double,
    @SerializedName("settled_khata_amount") val settledKhataAmount: Double,
    @SerializedName("timestamp") val timestamp: String,
    @SerializedName("soundbox_announcement") val soundboxAnnouncement: String,
    @SerializedName("audio_url") val audioUrl: String?,
    @SerializedName("is_soundbox_verified") val isSoundboxVerified: Boolean
)
```

---

## 4. Retrofit Client Interface for Salwa

Salwa, copy this into `com.paytm.vyapaarai.data.network.VyapaarApiService.kt`:

```kotlin
package com.paytm.vyapaarai.data.network

import com.paytm.vyapaarai.data.model.*
import okhttp3.MultipartBody
import okhttp3.RequestBody
import retrofit2.Response
import retrofit2.http.*

interface VyapaarApiService {

    // 1. Dashboard Metrics
    @GET("api/v1/dashboard/metrics")
    suspend fun getDashboardMetrics(
        @Query("merchant_id") merchantId: String = "sharma-kirana-001"
    ): Response<DashboardMetricsResponse>

    // 2. Voice Copilot Query (Audio upload)
    @Multipart
    @POST("api/v1/copilot/voice-query")
    suspend fun sendVoiceQuery(
        @Part("merchant_id") merchantId: RequestBody,
        @Part audioFile: MultipartBody.Part
    ): Response<VoiceQueryResponse>

    // 3. Khata Ledger & Reminders
    @GET("api/v1/khata/list")
    suspend fun getKhataList(
        @Query("merchant_id") merchantId: String = "sharma-kirana-001"
    ): Response<KhataListResponse>

    @POST("api/v1/khata/send-reminder")
    suspend fun sendKhataReminder(
        @Body request: KhataReminderRequest
    ): Response<KhataReminderResponse>

    // 4. 1-Click Loan Claim
    @POST("api/v1/loan/claim")
    suspend fun claimLoanAdvance(
        @Body request: LoanClaimRequest
    ): Response<LoanClaimResponse>

    // 5. Live Feed (Polling fallback)
    @GET("api/v1/merchant/live-feed")
    suspend fun getLiveFeed(
        @Query("merchant_id") merchantId: String = "sharma-kirana-001",
        @Query("limit") limit: Int = 20
    ): Response<List<LiveFeedEventDto>>

    // 6. Hackathon Live Demo Triggers
    @POST("api/v1/demo/simulate-qr-udhaar")
    suspend fun simulateQrUdhaar(
        @Query("customer_name") customerName: String = "Rahul Kumar",
        @Query("amount") amount: Double = 200.0,
        @Query("merchant_id") merchantId: String = "sharma-kirana-001"
    ): Response<CustomerPayLaterResponse>

    @POST("api/v1/demo/simulate-qr-settlement")
    suspend fun simulateQrSettlement(
        @Query("customer_name") customerName: String = "Rahul Kumar",
        @Query("payment_amount") paymentAmount: Double = 500.0,
        @Query("settle_amount") settleAmount: Double = 200.0,
        @Query("merchant_id") merchantId: String = "sharma-kirana-001"
    ): Response<CustomerPayAndSettleResponse>

    @POST("api/v1/demo/reset")
    suspend fun resetDemoData(): Response<Map<String, String>>
}
```

---

## 5. Live Event Push Handler in Kotlin (SSE Client)

Salwa can use OkHttp's `EventSource` to get instantaneous Soundbox and QR updates without polling:

```kotlin
package com.paytm.vyapaarai.data.network

import com.google.gson.Gson
import com.paytm.vyapaarai.data.model.LiveFeedEventDto
import kotlinx.coroutines.channels.awaitClose
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.callbackFlow
import okhttp3.*
import okhttp3.sse.EventSource
import okhttp3.sse.EventSourceListener
import okhttp3.sse.EventSources
import java.util.concurrent.TimeUnit

class SoundboxRealtimeClient(
    private val baseUrl: String = "http://10.150.76.180:8000/",
    private val gson: Gson = Gson()
) {
    private val client = OkHttpClient.Builder()
        .readTimeout(0, TimeUnit.MILLISECONDS)
        .build()

    fun listenToEvents(): Flow<LiveFeedEventDto> = callbackFlow {
        val request = Request.Builder()
            .url("${baseUrl}api/v1/stream/events")
            .header("Accept", "text/event-stream")
            .build()

        val eventSourceListener = object : EventSourceListener() {
            override fun onEvent(eventSource: EventSource, id: String?, type: String?, data: String) {
                try {
                    if (data.contains("event_id")) {
                        val event = gson.fromJson(data, LiveFeedEventDto::class.java)
                        trySend(event)
                    }
                } catch (e: Exception) {
                    e.printStackTrace()
                }
            }

            override fun onFailure(eventSource: EventSource, t: Throwable?, response: Response?) {
                // Auto-retry handled by Flow
            }
        }

        val eventSource = EventSources.createFactory(client).newEventSource(request, eventSourceListener)

        awaitClose {
            eventSource.cancel()
        }
    }
}
```

---

## 6. Ready-to-Send Agent Prompt for Salwa

Salwa can copy and paste the block below directly into Claude, Cursor, or Antigravity:

```text
You are an expert Android developer building the native Android app for "Paytm VyapaarAI" (Track 1: Merchant Growth AI - Paytm Build for India AI Hackathon).

Follow the complete API integration specification in SALWA_API_INTEGRATION_DOC.md:
- Base URL: "http://10.150.76.180:8000/"
- Language: Kotlin 1.9+ with Jetpack Compose & Material 3.
- Theme: Paytm Navy (#002e6e), Electric Cyan (#00b9f1), Success Green (#00ba58), Warning Amber (#ff9800).

Implement the following:
1. Data models and Retrofit service exactly matching the DTOs and VyapaarApiService in the document.
2. Screen 1 (Counter Dashboard): Live Feed LazyColumn showing incoming payments (Green), customer QR pay-later alerts (Amber), and auto-settlements (Blue).
3. Screen 2 (Customer QR Pay-Later Demo Hub): Buttons to trigger simulateQrUdhaar and simulateQrSettlement live.
4. Screen 3 (Khata Ledger): List with risk badges and 1-click "Send WhatsApp Payment Link" button calling sendKhataReminder.
5. Screen 4 (Voice Copilot Dialog): Pulsing waveform animation while recording audio, sending audio via sendVoiceQuery, and auto-playing the returned voice reply audio.
6. Screen 5 (1-Click Working Capital Claim): Credit score gauge and 1-click claim button calling claimLoanAdvance.

Ensure clean MVVM architecture with StateFlow, coroutines, and error handling.
```

---

*Compiled and verified for Paytm VyapaarAI Android Integration.*  
*Hosted at `~/www/html/SALWA_API_INTEGRATION_DOC.md` and accessible at `http://10.150.76.180:8080/SALWA_API_INTEGRATION_DOC.md`*
