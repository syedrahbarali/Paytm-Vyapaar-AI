# Paytm VyapaarAI — Master Engineering & Product Delivery Specification

**Hackathon Track:** Track 1 — Merchant Growth AI (Paytm Build for India AI Hackathon, Noida)  
**Document Target Audience:** Autonomous AI Agents (Claude / Antigravity), Android Developers, and UI/UX Product Designers.  
**Language Specification:** Strict English (Technical & Production Grade).

---

## 1. Executive Summary & Product Vision

### 1.1 The Core Mission
Transform the passive **Paytm Soundbox** from an audio notification buzzer ("₹X received on Paytm") into an **Active, Voice-First AI Financial Copilot and Visual Command Center** for over 1 Crore+ Indian retail and kirana merchants.

### 1.2 The Winning Product Formula: The Hardware-Mobile-WhatsApp Triad
1. **The Soundbox Hardware (Counter Audio Layer):** Functions as the physical ear and voice of the store. Announces instant payment arrivals and captures push-to-talk vernacular merchant queries via its LTE mic array.
2. **The Android Native Application (Merchant Visual Command Center):** Eliminates manual typing. Automatically syncs Soundbox streams in real-time, displays the verified Khata (customer credit) ledger, provides financial privacy, and executes 1-click underwriting workflows.
3. **The WhatsApp Customer Channel (Settlement Layer):** Serves as a zero-friction recovery pipeline. Customers receive dynamic Paytm UPI QR payment links directly on WhatsApp, with settlements routing back to the Soundbox.

---

## 2. Locked Core Capabilities (Scope Boundary)

```text
+--------------------------------------------------------------------------------------------------+
| SCOPE BOUNDARY: NO generic inventory scanning. NO manual accounting entries.                    |
| Every rupee and action is verified against live, deterministic Paytm QR & Soundbox transactions. |
+--------------------------------------------------------------------------------------------------+
```

1. **Feature 1: Passive Audio Payment Confirmation (Soundbox Ingestion)**
   - Customer scans Paytm QR at counter.
   - Soundbox sounds the 3W chime: *"Paytm par ₹150 prapt hue"*.
   - A real-time webhook immediately updates the append-only SQL database and pushes a green checkmark row to the Android app feed. Zero manual typing.
2. **Feature 2: Push-to-Talk Voice Business Intelligence**
   - Shopkeeper taps the Soundbox push-to-talk button or the floating app mic and speaks in Hinglish: *"Bhaiya aaj kitna bika aur pichle 1 ghante me kitna paisa aaya?"*
   - Acoustic noise gate cleans background traffic and shop chatter. Groq Whisper (<500ms) transcribes audio. Llama 3.3 70B parses the structured intent. Deterministic SQL computes the exact sales (`₹9,420`). Edge-TTS replies in natural Indian-accented Hindi/English within 3.5 seconds.
3. **Feature 3: Voice-Triggered Khata (Udhaar) Recovery Engine**
   - Merchant speaks: *"Ramesh aur Amit ko udhari ka reminder bhej do"*.
   - AI extracts target entities, looks up outstanding balances in the Khata database (Ramesh: ₹1,400, Amit: ₹850), and dispatches personalized WhatsApp messages with dynamic Paytm QR links.
   - When the customer clicks and settles the link, the Soundbox chimes and the Khata entry automatically marks as `SETTLED`.
4. **Feature 4: Proprietary Credit Health Scoring & 1-Click Cash Advance**
   - System evaluates daily transaction consistency, settlement frequency, and average ticket size into a 0–100 **Paytm Merchant Health Score**.
   - Merchants scoring above 75 unlock a pre-approved ₹50,000 Paytm Working Capital Advance.
   - Merchant claims the advance with 1-click OTP consent. Capital is instantly credited to their verified Paytm Payments Bank account. Repayments occur via a micro-daily sweep of ₹300 from daily QR settlements.

---

## 3. End-to-End System Architecture Diagram

```mermaid
flowchart TD
    subgraph Physical Counter
        Cust["Customer (Payer)"] -->|Scans QR| SB["Paytm Smart Soundbox (Hardware / IoT)"]
        Merch["Merchant (Shopkeeper)"] -->|Push-to-Talk Audio Note| SB
    end

    subgraph Mobile Interface (Salwa & Srishti)
        APP["Paytm VyapaarAI Android App\n(Kotlin + Jetpack Compose)"]
        Merch -->|Visual Oversight & 1-Click CTAs| APP
    end

    subgraph Backend Engine (Rahbar)
        GW["FastAPI Core Gateway (/api/v1)"]
        SB -->|LTE MQTT / Webhook POST| GW
        APP -->|Multipart Audio / REST JSON| GW

        subgraph AI Voice & Intent Pipeline
            NG["WebRTC Acoustic Noise Gate"]
            WHP["Groq Whisper-large-v3 (<500ms ASR)"]
            LLM["Llama 3.3 70B (Pydantic Schema Router)"]
            TTS["Edge-TTS Indian Accent Voice Generator"]
        end

        GW --> NG --> WHP --> LLM

        subgraph Deterministic Financial Core
            DB[("PostgreSQL / SQLite Immutable Ledger")]
            SCORE["Credit Underwriting & Scoring Engine (0-100)"]
        end

        LLM -->|Strict Parametric Query| DB
        DB --> SCORE
        DB --> TTS
    end

    subgraph External Action Rails
        TTS -->|Synthetic Audio Reply (.mp3)| SB
        TTS -->|Audio URL + Telemetry State| APP
        GW -->|Dynamic UPI QR Link| WA["Meta WhatsApp Cloud API"]
        WA -->|Delivers Khata Collection Link| Debtor["Debtor Customer (Ramesh)"]
        Debtor -->|Pays Outstanding Bill| SB
    end
```

---

## 4. Workstream 1: Requirements for Salwa (Android Lead)

### 4.1 Technology Stack & Setup
- **Programming Language:** Kotlin (1.9+)
- **UI Framework:** Jetpack Compose with Material 3 Design
- **Architecture Pattern:** MVVM (Model-View-ViewModel) with StateFlow
- **Networking:** Retrofit2 + OkHttp3 + Kotlinx Serialization / Gson
- **Audio Recording & Playback:** Android `MediaRecorder` (saving to `.m4a` / AAC) + `MediaPlayer` / `ExoPlayer`
- **Required Android Permissions:**
  ```xml
  <uses-permission android:name="android.permission.RECORD_AUDIO" />
  <uses-permission android:name="android.permission.INTERNET" />
  <uses-permission android:name="android.permission.MODIFY_AUDIO_SETTINGS" />
  ```

### 4.2 Exact Screen Implementations

#### Screen 1: Home Dashboard (Counter Mode)
- **Top Bar:** Store name (`Sharma Kirana Store`), green live status indicator (`Soundbox #SB-DELHI-981 Online`), notification bell.
- **Summary Hero Card:** Official Paytm Navy blue gradient (`#002e6e` to `#004394`). Displays today's total revenue (`₹9,420.00`), transaction count (`42 Txns`), peak footfall window (`6 - 8 PM`), and Credit Health Score (`88/100`).
- **Live Soundbox Feed:** A high-performance Compose `LazyColumn` showing real-time incoming payments. Each row displays customer name, payment mode badge (Paytm UPI / QR), timestamp, soundbox chime verification tag, and green amount (`+ ₹150`).
- **Khata Recovery Alert Banner:** Red left-bordered card highlighting overdue balances (`₹2,250 Pending`). Contains customer names with a prominent green *"📲 Send WA Link"* button.
- **Paytm Instant Loan Banner:** Light blue card highlighting the pre-approved ₹50,000 working capital loan with a direct action button.
- **Floating Action Button (FAB):** Centered floating microphone button above the bottom navigation bar with an official Paytm Cyan gradient (`#00b9f1` to `#002e6e`).

#### Screen 2: Voice Copilot Modal Overlay
- **Trigger:** Tapping the floating mic FAB or hardware Soundbox sync.
- **Visual Presentation:** Full-screen modal overlay with a dark navy blur scrim (`#001844` at 94% opacity).
- **Hero Graphic:** Realistic Paytm Soundbox 4.0 hardware digital twin illustration in the center, featuring the white Paytm logo badge, speaker grill, and glowing green LTE status LED.
- **Live Acoustic Waveform:** Dynamic pulsing bar visualizer providing feedback while the user speaks.
- **Transcription Card:** Real-time text display of the merchant's query (*"Bhaiya aaj kitna bika aur udhari kiski baaki hai?"*).
- **AI Voice Bubble:** Displays the synthesized response text with a speaker icon while the audio streams through the phone's loudspeaker.
- **Dynamic Action Buttons:** Quick action triggers (*"📲 Send Reminders to Ramesh & Amit"* and *"✕ Dismiss"*).

#### Screen 3: Khata (Udhaar) Recovery Directory
- **Header Summary Card:** Red gradient banner showing total uncollected credit (`₹2,250.00`) across overdue accounts.
- **Debtor List Cards:**
  - Card 1: `Ramesh General Store` | Phone: `+91 98765 43210` | Overdue: `12 Days` | Amount: `₹1,400` | Tag: `CRITICAL (Red)`.
  - Card 2: `Amit Kumar` | Phone: `+91 98112 23344` | Overdue: `4 Days` | Amount: `₹850` | Tag: `PENDING (Amber)`.
- **Action Buttons per Row:**
  - *"📲 Send WA Payment Link"* (WhatsApp green: `#25d366`): Calls backend API to dispatch link.
  - *"Cash Settle"*: Manual cash clearance fallback.

#### Screen 4: 1-Click Paytm Lending Claim Screen
- **Loan Hero Header:** Deep navy box displaying pre-approved limit (`₹50,000`), underwritten by Soundbox consistency.
- **Repayment Terms Grid:**
  - Daily Micro Sweep: `₹300 / day from QR settlements`
  - Monthly Interest Rate: `1.25% flat`
  - Repayment Tenure: `6 Months (180 Days)`
  - Documentation: `Zero Paperwork (0 ITR Required)`
- **Disbursal Confirmation:** Bank account ending in `*4821` (Paytm Payments Bank) with a bold cyan *"Claim ₹50,000 Advance Now"* button.

### 4.3 Retrofit Network Client Interface
Salwa must implement the following API contract in Kotlin:

```kotlin
interface VyapaarApiService {
    @Multipart
    @POST("api/v1/copilot/voice-query")
    suspend fun sendVoiceQuery(
        @Part("merchant_id") merchantId: RequestBody,
        @Part audioFile: MultipartBody.Part
    ): Response<VoiceQueryResponse>

    @POST("api/v1/khata/send-reminder")
    suspend fun triggerKhataReminder(
        @Body request: KhataReminderRequest
    ): Response<KhataReminderResponse>

    @POST("api/v1/loan/claim")
    suspend fun claimLoanAdvance(
        @Body request: LoanClaimRequest
    ): Response<LoanClaimResponse>

    @GET("api/v1/dashboard/metrics")
    suspend fun getDashboardMetrics(
        @Query("merchant_id") merchantId: String
    ): Response<DashboardMetricsResponse>
}
```

---

## 5. Workstream 2: Requirements for Srishti (UI/UX Lead)

### 5.1 Official Paytm Brand Color Tokens
Srishti must enforce the authentic Paytm for Business brand palette across all Figma frames:
- **Paytm Deep Navy:** `#002e6e` (Primary brand color, headers, primary buttons)
- **Paytm Dark Header Gradient:** `#002970` to `#001844`
- **Paytm Electric Cyan:** `#00b9f1` (Accents, active pills, floating mic gradient, hero CTAs)
- **Paytm App Canvas Background:** `#f3f7fa` (The authentic soft greyish-blue tint of Paytm for Business)
- **Pure White Cards:** `#ffffff` with structural border `#e2ebf8`
- **Growth / Verification Green:** `#10b981` / `#22c55e` (Verified tags, positive amounts)
- **Overdue Alert Red:** `#ef4444` / `#b91c1c` (Critical Khata tags, uncollected revenue alerts)
- **Official WhatsApp Green:** `#25d366` (Customer collection CTAs)

### 5.2 Mandatory Typography Rules
- **Font Family:** Open Sans / Inter
- **Hero Numbers (Sales/Loan):** 30pt - 36pt, ExtraBold (800 / 900)
- **Section Headers:** 12pt - 14pt, Bold (700), All Caps with 0.5px letter-spacing
- **Body / Metadata:** 10pt - 12pt, Regular / Medium (400 / 500)

### 5.3 Concrete Figma Deliverables Checklist
1. **Frame 1 (390 x 800 px):** `Home_Dashboard_Counter_Mode`
   - Includes real-time Soundbox status pill, ₹9,420 summary card, 3 feed items, Khata alert box, and loan teaser.
2. **Frame 2 (390 x 800 px):** `Voice_Copilot_Modal_Overlay`
   - Dark modal scrim (`#001844`), central Paytm Soundbox hardware vector with speaker grill and LED, pulsing cyan waveform, and dual transcription bubbles.
3. **Frame 3 (390 x 800 px):** `Khata_Directory_Screen`
   - Trapped capital banner (`₹2,250`), individual debtor cards with overdue badges and WhatsApp share buttons.
4. **Frame 4 (390 x 800 px):** `Paytm_Lending_Claim_Modal`
   - ₹50,000 cash advance terms table, daily ₹300 sweep explanation, and 1-click claim button.
5. **Frame 5 (Customer WhatsApp View):**
   - Mockup of the debtor's WhatsApp chat screen showing the inbound Paytm payment link and dynamic QR code image.

---

## 6. Workstream 3: Requirements for Rahbar (Backend & AI Lead)

### 6.1 Technology Stack & Python Environment
- **Framework:** Python 3.11+ with FastAPI & Uvicorn (ASGI)
- **Database Engine:** PostgreSQL (Supabase / Docker) with SQLAlchemy 2.0 (Async) + Alembic
- **Validation Engine:** Pydantic v2 (Strict Schema Enforcement)
- **Speech Recognition (ASR):** Groq Cloud API (`whisper-large-v3`) — sub-500ms transcription
- **Intent Router:** Llama 3.3 70B (via Groq) utilizing structured tool-calling / JSON mode
- **Speech Synthesis (TTS):** Edge-TTS / gTTS producing Hinglish/Hindi audio buffers
- **WhatsApp Gateway:** Meta WhatsApp Cloud API (with dynamic local fallback payment URLs)

### 6.2 Database Schemas (DDL & Entity Relationships)

```sql
-- 1. Merchants Table
CREATE TABLE merchants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_name VARCHAR(120) NOT NULL,
    phone_number VARCHAR(15) UNIQUE NOT NULL,
    soundbox_device_id VARCHAR(50) UNIQUE NOT NULL,
    health_score INT DEFAULT 88,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. Transactions Table (Append-Only Immutable Ledger)
CREATE TABLE transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    merchant_id UUID REFERENCES merchants(id) ON DELETE CASCADE,
    idempotency_key VARCHAR(80) UNIQUE NOT NULL,
    amount NUMERIC(10, 2) NOT NULL,
    payment_mode VARCHAR(20) DEFAULT 'UPI',
    payer_name VARCHAR(100),
    status VARCHAR(20) DEFAULT 'SUCCESS',
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_transactions_merchant_timestamp ON transactions(merchant_id, timestamp);

-- 3. Khata Entries Table (Customer Credit Ledger)
CREATE TABLE khata_entries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    merchant_id UUID REFERENCES merchants(id) ON DELETE CASCADE,
    customer_name VARCHAR(100) NOT NULL,
    customer_phone VARCHAR(15) NOT NULL,
    amount_due NUMERIC(10, 2) NOT NULL,
    due_date DATE NOT NULL,
    status VARCHAR(20) DEFAULT 'PENDING', -- PENDING, REMINDED, SETTLED
    last_reminder_sent TIMESTAMP WITH TIME ZONE
);

-- 4. Loan Underwriting Table
CREATE TABLE loan_applications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    merchant_id UUID REFERENCES merchants(id) ON DELETE CASCADE,
    pre_approved_amount NUMERIC(10, 2) NOT NULL,
    daily_sweep_amount NUMERIC(10, 2) DEFAULT 300.00,
    interest_rate_pct NUMERIC(4, 2) DEFAULT 1.25,
    tenure_months INT DEFAULT 6,
    status VARCHAR(25) DEFAULT 'OFFERED' -- OFFERED, CLAIMED, DISBURSED
);
```

### 6.3 Complete REST API Specifications

#### Endpoint 1: Simulated Soundbox Payment Webhook
- **Route:** `POST /api/v1/soundbox/webhook`
- **Payload:**
  ```json
  {
    "soundbox_device_id": "SB-DELHI-981",
    "idempotency_key": "TXN_UPI_982194821",
    "amount": 150.00,
    "payer_name": "Aakash Gupta",
    "payment_mode": "UPI",
    "timestamp": "2026-10-30T10:14:22Z"
  }
  ```
- **Response (201 Created):**
  ```json
  {
    "status": "SUCCESS",
    "transaction_id": "e4a7a8d2-1b1e-4b71-9c6a-4d2a1b1e4b71",
    "updated_metrics": {
      "today_total_sales": 9570.00,
      "today_txn_count": 43,
      "soundbox_chime": "Paytm par 150 rupaye prapt hue"
    }
  }
  ```

#### Endpoint 2: Voice Copilot Audio Pipeline
- **Route:** `POST /api/v1/copilot/voice-query`
- **Request Type:** `multipart/form-data` (`merchant_id: string`, `audio_file: binary .m4a/.wav`)
- **Execution Lifecycle:**
  1. Temporary audio buffer write + WebRTC noise suppression.
  2. Groq Whisper inference $\rightarrow$ Transcribes Hinglish text.
  3. Llama 3.3 70B Structured Intent Extraction $\rightarrow$ returns Enum: `[DAILY_SUMMARY, KHATA_QUERY, LOAN_STATUS, UNKNOWN]`.
  4. Triggers deterministic PostgreSQL aggregate query (Zero LLM math).
  5. Edge-TTS synthesizes Hindi/Indian-English audio file into static storage.
- **Response (200 OK):**
  ```json
  {
    "status": "SUCCESS",
    "transcription": "Bhaiya aaj kitna bika aur udhari kiski baaki hai?",
    "intent": "DAILY_SUMMARY_AND_KHATA",
    "voice_reply_audio_url": "https://api.vyapaarai.in/static/replies/rep_9281.mp3",
    "voice_reply_transcript": "Sharma ji, aaj total ₹9,420 ki sale hui hai aur 2 customers ka ₹2,250 udhaar baaki hai.",
    "data_payload": {
      "today_total_sales": 9420.00,
      "today_txn_count": 42,
      "total_khata_pending": 2250.00,
      "overdue_customers": [
        {
          "khata_id": "8f8b3c21-...",
          "name": "Ramesh General Store",
          "amount": 1400.00,
          "days_overdue": 12
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

#### Endpoint 3: 1-Click WhatsApp Khata Reminder Dispatcher
- **Route:** `POST /api/v1/khata/send-reminder`
- **Payload:** `{"khata_id": "8f8b3c21-4d2a-4b71-9c6a-1b1e4b71a8d2"}`
- **Execution:** Dispatches Meta WhatsApp Cloud API template message containing customer name, pending debt, and dynamic Paytm UPI QR payment link.
- **Response (200 OK):**
  ```json
  {
    "status": "DELIVERED",
    "recipient": "+919876543210",
    "payment_link": "https://p.paytm.me/qr/pay?amt=1400.00&ref=KHATA_8F8B"
  }
  ```

#### Endpoint 4: Instant Loan Disbursal Pipeline
- **Route:** `POST /api/v1/loan/claim`
- **Payload:** `{"merchant_id": "11223344-...", "amount": 50000.00, "otp_consent": "849201"}`
- **Response (200 OK):**
  ```json
  {
    "status": "DISBURSED",
    "disbursal_id": "LN_PTM_88192839",
    "credited_to": "Paytm Payments Bank **********4821",
    "disbursed_at": "2026-10-30T10:16:02Z"
  }
  ```

---

## 7. Judge Cross-Examination Defense Matrix

Be prepared to answer these exact questions during the live finals at Paytm HQ:

| Tough Judge Question | Winning Technical Defense |
| :--- | :--- |
| *"Soundbox has always announced payments. What is actually new here?"* | **"Current soundboxes are passive, one-way loudspeakers.** They cannot answer business questions, cannot track uncollected credit, and cannot help merchants secure working capital. We transformed the Soundbox into a **two-way AI business partner** that listens to push-to-talk queries, automates WhatsApp debt collection, and turns verified UPI streams into pre-approved loans." |
| *"What happens if the LLM hallucinates an incorrect sales number?"* | **"The LLM is completely isolated from arithmetic.** We enforce a strict separation of concerns: Llama 3.3 is purely an NLP intent parser. All financial metrics, sums, and debt balances are computed deterministically inside an append-only PostgreSQL database. 0% calculation hallucination." |
| *"Why not build a standalone web SaaS or Khatabook clone?"* | **"Bharat kirana merchants operate on busy counters and will never type on keyboards or web dashboards.** Khatabook requires manual bookkeeping that merchants abandon after two weeks. By tying directly into the Soundbox and WhatsApp, our solution requires **zero manual data entry**." |
| *"How do you handle background traffic and shop blender noise?"* | **"We utilize an acoustic WebRTC noise-gate filter with spectral subtraction.** Incoming audio is cleaned of ambient street noise before passing to Groq Whisper-large-v3, maintaining over 94% Hinglish transcription accuracy." |
| *"How will Paytm prevent defaults on these pre-approved merchant loans?"* | **"Repayments are non-intrusive and automated via a daily micro-sweep of ₹300 directly from incoming Soundbox QR settlements.** Paytm collects before funds settle to the merchant, eliminating collection agent overhead and lowering default rates." |

---

## 8. Final Stage Demonstration Sequence (2-Minute Script)

1. **0:00 - 0:30 (The Live IoT Hook):** Judge scans the demo QR code on the counter. The simulated Soundbox plays the loud chime: *"Paytm par ₹150 prapt hue"*. The Android app instantly flashes a green row on the live feed.
2. **0:30 - 1:00 (The Push-to-Talk AI Query):** Presenter holds the Soundbox button: *"Bhaiya aaj kitna bika aur udhari kiski baaki hai?"* Soundbox speaks back in 2.5 seconds: *"Sharma ji, aaj total ₹9,420 ki sale hui hai aur 2 customers ka ₹2,250 udhaar baaki hai."*
3. **1:00 - 1:30 (The WhatsApp Khata Action):** Presenter taps *"Send WhatsApp Link"* on the app. The debtor's live phone beeps with an official WhatsApp message and dynamic payment QR.
4. **1:30 - 2:00 (The Paytm Revenue Closer):** Presenter shows the pre-approved ₹50,000 Paytm Cash Advance card, explaining the 2.5% origination fee and Soundbox retention moat for Paytm.
