# Paytm VyapaarAI — Agent Integration Manifest for Salwa (Android)

> **Agent Instruction:** This manifest is machine-readable and human-verifiable. Any Antigravity / autonomous Android coding agent working on the Kotlin client must use the specifications, endpoints, data contracts, and Retrofit interfaces below to wire up the Android Jetpack Compose screens.

---

## 1. Service Runtime & Environment Configuration

| Property | Value | Description |
| :--- | :--- | :--- |
| **Service Name** | `Paytm VyapaarAI Core Engine` | FastAPI Backend |
| **Emulator Base URL** | `http://10.0.2.2:8000` | Android Virtual Device (AVD) loopback |
| **Physical Device Base URL** | `http://<HOST_IP>:8000` | Physical Android device over local Wi-Fi |
| **API Path Prefix** | `/api/v1` | All v1 endpoints are prefixed with `/api/v1` |
| **Interactive OpenAPI Docs** | `http://127.0.0.1:8000/docs` | Live Swagger UI |
| **OpenAPI Schema Spec** | `file:///home/syed-rahbar-ali/Desktop/Paytm-Hackthon/backend/openapi.json` | Full OpenAPI v3.1 schema |
| **Default Merchant ID** | `sharma-kirana-001` | Sharma Kirana Store (Default counter) |
| **Default Soundbox ID** | `SB-DELHI-981` | Paytm Smart Soundbox 4.0 |

---

## 2. API Endpoint Matrix

| # | Endpoint Route | HTTP Method | Request Content-Type | Target Android UI Screen | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1** | `/api/v1/dashboard/metrics` | `GET` | N/A | **Screen 1 (Home Dashboard)** | Fetch today's sales (`₹9,420`), 42 transactions, credit health score (`88`), Khata summary badge, and pre-approved loan card. |
| **2** | `/api/v1/copilot/voice-query` | `POST` | `multipart/form-data` | **Screen 2 (Voice Copilot Modal)** | Upload spoken audio from floating mic FAB. Returns transcription, intent, synthesis audio reply URL (`.mp3`), and fresh ledger metrics. |
| **3** | `/api/v1/khata/list` | `GET` | N/A | **Screen 3 (Khata Directory)** | List all outstanding customer credit accounts (`Ramesh General Store` ₹1,400, `Amit Kumar` ₹850). |
| **4** | `/api/v1/khata/send-reminder` | `POST` | `application/json` | **Screen 3 & Dashboard Banner** | 1-click trigger to dispatch WhatsApp collection message with dynamic Paytm UPI QR payment link to debtor. |
| **5** | `/api/v1/loan/claim` | `POST` | `application/json` | **Screen 4 (1-Click Loan Modal)** | Disburses pre-approved ₹50,000 working capital loan with daily ₹300 micro-sweep from QR collections. |
| **6** | `/api/v1/soundbox/webhook` | `POST` | `application/json` | **Counter IoT / Live Demo Action** | Ingests counter QR payment, returns Soundbox chime text (*"Paytm par ₹150 prapt hue"*), and updates real-time feed. |

---

## 3. Detailed Request & Response Specifications

### 3.1 Endpoint 1: Dashboard Metrics
- **Method & Path:** `GET /api/v1/dashboard/metrics?merchant_id={merchant_id}`
- **Query Params:**
  - `merchant_id` (string, required): e.g. `"sharma-kirana-001"`
- **Response Format (`200 OK`):**
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
    "total_sales": 9570.0,
    "transaction_count": 43,
    "peak_hour": "6:00 PM - 8:00 PM"
  },
  "recent_transactions": [
    {
      "id": "txn_101",
      "payer_name": "Aakash Gupta",
      "amount": 150.0,
      "payment_mode": "Paytm UPI",
      "timestamp": "2026-10-31T06:17:56.307299",
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

### 3.2 Endpoint 2: Voice Copilot Audio Pipeline
- **Method & Path:** `POST /api/v1/copilot/voice-query`
- **Content-Type:** `multipart/form-data`
- **Form Fields:**
  - `merchant_id` (string): `"sharma-kirana-001"`
  - `audio_file` (binary): Audio recording (`.m4a`, `.wav`, or `.aac`)
- **Response Format (`200 OK`):**
```json
{
  "status": "SUCCESS",
  "transcription": "Bhaiya aaj kitna bika aur udhari kiski baaki hai?",
  "intent": "DAILY_SUMMARY_AND_KHATA",
  "voice_reply_audio_url": "http://10.0.2.2:8000/static/audio/reply_ca42da96.mp3",
  "voice_reply_transcript": "Sharma ji, aaj counter par total ₹9,570 ki sale hui hai, aur 2 customers ka ₹2,250 udhaar baaki hai.",
  "data_payload": {
    "today_total_sales": 9570.0,
    "today_txn_count": 43,
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

### 3.3 Endpoint 3: Khata Recovery Directory
- **Method & Path:** `GET /api/v1/khata/list?merchant_id={merchant_id}`
- **Query Params:**
  - `merchant_id` (string, required): e.g. `"sharma-kirana-001"`
- **Response Format (`200 OK`):**
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

### 3.4 Endpoint 4: 1-Click WhatsApp Reminder Trigger
- **Method & Path:** `POST /api/v1/khata/send-reminder`
- **Content-Type:** `application/json`
- **Request Body:**
```json
{
  "khata_id": "khata_001"
}
```
- **Response Format (`200 OK`):**
```json
{
  "status": "DELIVERED",
  "khata_id": "khata_001",
  "recipient": "+919876543210",
  "customer_name": "Ramesh General Store",
  "payment_link": "https://p.paytm.me/qr/pay?amt=1400.00&ref=KHATA_KHATA_001",
  "sent_at": "2026-10-31T06:22:56.241512+00:00"
}
```

---

### 3.5 Endpoint 5: 1-Click Lending Claim
- **Method & Path:** `POST /api/v1/loan/claim`
- **Content-Type:** `application/json`
- **Request Body:**
```json
{
  "merchant_id": "sharma-kirana-001",
  "amount": 50000.0,
  "otp_consent": "849201"
}
```
- **Response Format (`200 OK`):**
```json
{
  "status": "DISBURSED",
  "disbursal_id": "LN_PTM_5B55106F",
  "amount": 50000.0,
  "credited_to": "Paytm Payments Bank **********4821",
  "daily_sweep_amount": 300.0,
  "disbursed_at": "2026-10-31T06:22:56.247192+00:00",
  "message": "₹50,000 has been credited to your Paytm Payments Bank account. Micro-sweep of ₹300/day activated."
}
```

---

### 3.6 Endpoint 6: Soundbox Transaction Webhook
- **Method & Path:** `POST /api/v1/soundbox/webhook`
- **Content-Type:** `application/json`
- **Request Body:**
```json
{
  "soundbox_device_id": "SB-DELHI-981",
  "idempotency_key": "TXN_UPI_SAMPLE_981",
  "amount": 150.0,
  "payer_name": "Aakash Gupta",
  "payment_mode": "Paytm UPI",
  "timestamp": "2026-10-31T06:20:00Z"
}
```
- **Response Format (`201 Created`):**
```json
{
  "status": "SUCCESS",
  "transaction_id": "txn_8b19f012",
  "soundbox_chime": "Paytm par ₹150 prapt hue",
  "updated_metrics": {
    "today_total_sales": 9570.0,
    "today_txn_count": 43
  }
}
```

---

## 4. Drop-in Kotlin Retrofit Client & Models

Salwa's Antigravity CLI agent can directly generate or verify the following Kotlin source file:

```kotlin
package com.paytm.vyapaarai.data.api

import okhttp3.MultipartBody
import okhttp3.RequestBody
import retrofit2.Response
import retrofit2.http.*

interface VyapaarApiService {

    @GET("api/v1/dashboard/metrics")
    suspend fun getDashboardMetrics(
        @Query("merchant_id") merchantId: String = "sharma-kirana-001"
    ): Response<DashboardMetricsResponse>

    @Multipart
    @POST("api/v1/copilot/voice-query")
    suspend fun sendVoiceQuery(
        @Part("merchant_id") merchantId: RequestBody,
        @Part audioFile: MultipartBody.Part
    ): Response<VoiceQueryResponse>

    @GET("api/v1/khata/list")
    suspend fun getKhataList(
        @Query("merchant_id") merchantId: String = "sharma-kirana-001"
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

// -------------------------------------------------------------------------
// Kotlin DTO Data Classes
// -------------------------------------------------------------------------

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

data class KhataReminderRequest(
    val khata_id: String
)

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
    val timestamp: String? = null
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
