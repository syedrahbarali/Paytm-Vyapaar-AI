# Paytm VyapaarAI — API Reference & Integration Documentation

Comprehensive API documentation for the **Paytm VyapaarAI** system, powering the Android Merchant Application, the Hardware Soundbox sync, and WhatsApp collection pipelines.

---

## Table of Contents
1. [Overview & Base Configuration](#1-overview--base-configuration)
2. [Authentication & Merchant Context](#2-authentication--merchant-context)
3. [Endpoints Detailed Specification](#3-endpoints-detailed-specification)
   - [3.1 GET /api/v1/dashboard/metrics](#31-get-apiv1dashboardmetrics)
   - [3.2 POST /api/v1/copilot/voice-query](#32-post-apiv1copilotvoice-query)
   - [3.3 GET /api/v1/khata/list](#33-get-apiv1khatalist)
   - [3.4 POST /api/v1/khata/send-reminder](#34-post-apiv1khatasend-reminder)
   - [3.5 POST /api/v1/loan/claim](#35-post-apiv1loanclaim)
   - [3.6 POST /api/v1/soundbox/webhook](#36-post-apiv1soundboxwebhook)
4. [Error Codes & Responses](#4-error-codes--responses)
5. [cURL Integration Examples](#5-curl-integration-examples)

---

## 1. Overview & Base Configuration

- **Environment Base URLs:**
  - Local Dev / Android Emulator: `http://10.0.2.2:8000`
  - Local Wi-Fi / Physical Device: `http://<HOST_LOCAL_IP>:8000`
  - Production / Cloud: `https://api.vyapaarai.in`
- **Default Prefix:** `/api/v1`
- **Standard Protocol:** HTTP/1.1 or HTTP/2 over TLS
- **Content-Type:** `application/json` (unless specified as `multipart/form-data`)

---

## 2. Authentication & Merchant Context

For hackathon and fast integration, endpoints accept a deterministic `merchant_id` parameter (`sharma-kirana-001` by default).

Default Demo Context:
- **Merchant ID:** `sharma-kirana-001`
- **Business Name:** `Sharma Kirana Store`
- **Soundbox Device ID:** `SB-DELHI-981`
- **Base Credit Health Score:** `88/100`

---

## 3. Endpoints Detailed Specification

### 3.1 `GET /api/v1/dashboard/metrics`
Retrieves live aggregated metrics, real-time incoming transaction feed, credit health score, and loan eligibility for the merchant's home counter view.

#### Request
- **Method:** `GET`
- **URL:** `/api/v1/dashboard/metrics`
- **Query Parameters:**
  | Parameter | Type | Required | Description |
  | :--- | :--- | :--- | :--- |
  | `merchant_id` | `string` | **Yes** | Identifier of the merchant (e.g. `sharma-kirana-001`) |

#### Response (`200 OK`)
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

### 3.2 `POST /api/v1/copilot/voice-query`
Receives vernacular spoken audio (Hindi / Hinglish / English), transcribes via Groq Whisper (<500ms), determines query intent with Llama 3.3, computes deterministic ledger figures, and synthesizes a high-fidelity voice reply with Edge-TTS.

#### Request
- **Method:** `POST`
- **URL:** `/api/v1/copilot/voice-query`
- **Content-Type:** `multipart/form-data`
- **Form Data Fields:**
  | Field | Type | Required | Description |
  | :--- | :--- | :--- | :--- |
  | `merchant_id` | `text` | **Yes** | Merchant identifier |
  | `audio_file` | `file` | **Yes** | Voice note recorded via Android (`.m4a`, `.wav`, `.aac`, `.mp3`) |

#### Response (`200 OK`)
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

### 3.3 `GET /api/v1/khata/list`
Fetches all overdue customer credit accounts for the merchant's store, sorted by urgency and overdue age.

#### Request
- **Method:** `GET`
- **URL:** `/api/v1/khata/list`
- **Query Parameters:**
  | Parameter | Type | Required | Description |
  | :--- | :--- | :--- | :--- |
  | `merchant_id` | `string` | **Yes** | Merchant identifier |

#### Response (`200 OK`)
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

---

### 3.4 `POST /api/v1/khata/send-reminder`
Dispatches an official WhatsApp reminder containing a dynamic Paytm UPI QR payment link to the selected debtor.

#### Request
- **Method:** `POST`
- **URL:** `/api/v1/khata/send-reminder`
- **Content-Type:** `application/json`
- **Request Body:**
```json
{
  "khata_id": "khata_001"
}
```

#### Response (`200 OK`)
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

### 3.5 `POST /api/v1/loan/claim`
Disburses the pre-approved working capital loan to the merchant's verified Paytm Payments Bank account with 1-click OTP consent.

#### Request
- **Method:** `POST`
- **URL:** `/api/v1/loan/claim`
- **Content-Type:** `application/json`
- **Request Body:**
```json
{
  "merchant_id": "sharma-kirana-001",
  "amount": 50000.00,
  "otp_consent": "849201"
}
```

#### Response (`200 OK`)
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

### 3.6 `POST /api/v1/soundbox/webhook`
Simulates or receives an inbound counter payment event from the hardware Paytm Smart Soundbox. Automatically updates the database ledger, plays the speaker chime, and updates dashboard metrics.

#### Request
- **Method:** `POST`
- **URL:** `/api/v1/soundbox/webhook`
- **Content-Type:** `application/json`
- **Request Body:**
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

#### Response (`201 Created`)
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

## 4. Error Codes & Responses

Standard HTTP status codes are returned:
- `400 Bad Request`: Missing mandatory parameters or invalid format.
- `404 Not Found`: Merchant ID or Khata ID not found.
- `422 Unprocessable Entity`: Validation failure on input schema.
- `500 Internal Server Error`: Backend error (fallback responses provided).

Standard error payload format:
```json
{
  "detail": "Khata entry with ID 'khata_999' not found."
}
```

---

## 5. cURL Integration Examples

### Fetch Dashboard
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/dashboard/metrics?merchant_id=sharma-kirana-001"
```

### Trigger Khata WhatsApp Reminder
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/khata/send-reminder" \
     -H "Content-Type: application/json" \
     -d '{"khata_id": "khata_001"}'
```

### Claim Loan Advance
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/loan/claim" \
     -H "Content-Type: application/json" \
     -d '{"merchant_id": "sharma-kirana-001", "amount": 50000.0, "otp_consent": "849201"}'
```

### Simulate Soundbox Transaction
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/soundbox/webhook" \
     -H "Content-Type: application/json" \
     -d '{
       "soundbox_device_id": "SB-DELHI-981",
       "idempotency_key": "TXN_UPI_'$(date +%s)'",
       "amount": 150.0,
       "payer_name": "Aakash Gupta",
       "payment_mode": "UPI",
       "timestamp": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"
     }'
```

---

## 6. Customer-Initiated QR Pay-Later & Auto-Settlement Endpoints

### 6.1 GET `/checkout/{merchant_id}`
- **Description:** Renders the mobile-responsive Paytm-branded Smart Checkout web application for customers who scan the store's counter QR code.
- **Response:** `text/html` (Interactive web UI with live audio announcement support).

### 6.2 GET `/api/v1/customer/checkout-details/{merchant_id}`
- **Description:** Returns store information and automatically checks if the scanning customer's phone number has an active pending balance.
- **Query Parameters:** `customer_phone` (e.g. `+919811229988`)
- **Response Example:**
  ```json
  {
    "merchant_id": "sharma-kirana-001",
    "business_name": "Sharma Kirana Store",
    "soundbox_device_id": "SB-DELHI-981",
    "soundbox_online": true,
    "pending_khata": {
      "has_pending": true,
      "khata_id": "khata_qr_8f697aa4",
      "customer_name": "Vikas Sharma",
      "amount_due": 250.0,
      "due_date": "2026-11-07",
      "days_overdue": 0,
      "message": "Outstanding Khata: ₹250.0"
    },
    "supported_payment_modes": ["Paytm UPI", "GPay", "PhonePe", "BHIM UPI"],
    "checkout_url": "/checkout/sharma-kirana-001"
  }
  ```

### 6.3 POST `/api/v1/customer/pay-later`
- **Description:** Records customer-initiated Khata (credit) when the customer confirms credit on their own phone.
- **Request Body:**
  ```json
  {
    "merchant_id": "sharma-kirana-001",
    "customer_name": "Rahul Kumar",
    "customer_phone": "+919811229988",
    "amount": 200.0,
    "notes": "Evening groceries"
  }
  ```
- **Response Example:**
  ```json
  {
    "status": "RECORDED",
    "khata_id": "khata_qr_8f697aa4",
    "merchant_id": "sharma-kirana-001",
    "customer_name": "Rahul Kumar",
    "amount": 200.0,
    "soundbox_announcement": "Sharma Kirana alert: Rahul Kumar ne 200 rupaye ka udhaar darj kiya!",
    "audio_url": "/static/audio/reply_7d199d71.mp3",
    "timestamp": "2026-10-31T09:02:36.010247+00:00",
    "message": "₹200.0 credit recorded for Rahul Kumar. Soundbox verified."
  }
  ```

### 6.4 POST `/api/v1/customer/pay-and-settle`
- **Description:** Processes a return payment from a customer, automatically clearing pending Khata and crediting the remainder as a new sale.
- **Request Body:**
  ```json
  {
    "merchant_id": "sharma-kirana-001",
    "customer_name": "Rahul Kumar",
    "customer_phone": "+919811229988",
    "total_payment": 500.0,
    "settle_khata": true,
    "payment_mode": "Paytm UPI"
  }
  ```
- **Response Example:**
  ```json
  {
    "status": "SUCCESS",
    "transaction_id": "txn_settle_08251030",
    "merchant_id": "sharma-kirana-001",
    "customer_name": "Rahul Kumar",
    "total_payment": 500.0,
    "khata_settled_amount": 200.0,
    "net_new_purchase": 300.0,
    "soundbox_announcement": "Paytm par 500 rupaye prapt hue. Aur purana 200 rupaye udhaar chukta hua!",
    "audio_url": "/static/audio/reply_673f4a4e.mp3",
    "khata_status": "SETTLED",
    "timestamp": "2026-10-31T09:02:49.996011+00:00",
    "message": "Payment processed and Soundbox voice chime triggered."
  }
  ```

### 6.5 GET `/api/v1/merchant/counter-qr`
- **Description:** Generates and returns a 370x370 PNG image of the official Paytm Counter QR code that embeds the store checkout URL (`/checkout/{merchant_id}`).
- **Content-Type:** `image/png`

### 6.6 GET `/api/v1/merchant/live-feed`
- **Description:** Returns the real-time event feed for the merchant's Android app (payments, new khata requests, and settled khata).
- **Response:** Array of `LiveFeedEventDto` objects.

### 6.7 GET `/api/v1/stream/events`
- **Description:** Server-Sent Events (SSE) stream delivering real-time JSON events to Android or web dashboards.
- **Content-Type:** `text/event-stream`
