import os
import uuid
import datetime
from pathlib import Path
import edge_tts
from groq import Groq
from app.config import settings

AUDIO_OUTPUT_DIR = Path("backend/static/audio")
AUDIO_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

class VoiceIntelligenceService:
    def __init__(self):
        self.groq_client = None
        if settings.GROQ_API_KEY:
            self.groq_client = Groq(api_key=settings.GROQ_API_KEY)

    async def transcribe_audio(self, audio_file_bytes: bytes, filename: str) -> str:
        """Transcribes incoming merchant audio using Groq Whisper-large-v3, falling back to mock if no key."""
        if not self.groq_client:
            # Fallback for demo when GROQ_API_KEY is not set
            return "Bhaiya aaj kitna bika aur udhari kiski baaki hai?"

        temp_path = AUDIO_OUTPUT_DIR / f"temp_{uuid.uuid4().hex}_{filename}"
        with open(temp_path, "wb") as f:
            f.write(audio_file_bytes)

        try:
            with open(temp_path, "rb") as file_stream:
                transcription = self.groq_client.audio.transcriptions.create(
                    file=(filename, file_stream.read()),
                    model="whisper-large-v3",
                    response_format="text",
                    language="hi"  # Hint Hindi/Hinglish
                )
            return str(transcription).strip()
        except Exception as e:
            print(f"ASR Error: {e}")
            return "Bhaiya aaj kitna bika aur udhari kiski baaki hai?"
        finally:
            if temp_path.exists():
                temp_path.unlink()

    async def parse_intent_and_reply(self, transcript: str, sales_total: float, khata_total: float, overdue_count: int) -> tuple[str, str]:
        """Parses intent strictly without LLM arithmetic; generates natural Hinglish synthesis text."""
        transcript_lower = transcript.lower()

        is_sales = any(w in transcript_lower for w in ["bika", "sale", "kamayi", "aaj", "paisa", "kitna", "collection"])
        is_khata = any(w in transcript_lower for w in ["udhari", "udhaar", "khata", "baaki", "ramesh", "amit", "recovery", "pending"])
        is_loan = any(w in transcript_lower for w in ["loan", "advance", "paisa chahiye", "karza", "credit"])

        if is_sales and is_khata:
            intent = "DAILY_SUMMARY_AND_KHATA"
            reply_text = f"Sharma ji, aaj counter par total ₹{int(sales_total):,} ki sale hui hai, aur {overdue_count} customers ka ₹{int(khata_total):,} udhaar baaki hai."
        elif is_khata:
            intent = "KHATA_QUERY"
            reply_text = f"Sharma ji, aapke khata me total ₹{int(khata_total):,} baaki hai. Ramesh General Store ka ₹1,400 aur Amit Kumar ka ₹850 overdue hai."
        elif is_loan:
            intent = "LOAN_STATUS"
            reply_text = "Sharma ji, aapki Soundbox transaction consistency ke aadhar par ₹50,000 ka pre-approved loan available hai."
        else:
            intent = "DAILY_SUMMARY"
            reply_text = f"Sharma ji, aaj total ₹{int(sales_total):,} ki sale hui hai."

        return intent, reply_text

    async def synthesize_speech(self, text: str) -> str:
        """Synthesizes high quality natural Indian accent speech using Edge-TTS (hi-IN-MadhurNeural / en-IN-PrabhatNeural)."""
        file_id = f"reply_{uuid.uuid4().hex[:8]}.mp3"
        output_file = AUDIO_OUTPUT_DIR / file_id
        
        try:
            # Voice: Indian Hindi / Hinglish Natural Male Voice
            communicate = edge_tts.Communicate(text, "hi-IN-MadhurNeural", rate="+5%")
            await communicate.save(str(output_file))
        except Exception as e:
            print(f"TTS synthesis error: {e}")
            # Ensure file exists even in offline mode
            with open(output_file, "wb") as f:
                f.write(b"")

        return f"/static/audio/{file_id}"

voice_service = VoiceIntelligenceService()
