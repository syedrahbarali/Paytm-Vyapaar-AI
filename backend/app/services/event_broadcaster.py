import asyncio
import datetime
import json
from typing import AsyncGenerator, List, Dict, Any
from app.services.voice_service import voice_service

class SoundboxEventBroadcaster:
    def __init__(self, max_history: int = 50):
        self._subscribers: List[asyncio.Queue] = []
        self._history: List[Dict[str, Any]] = []
        self._max_history = max_history

    async def broadcast_event(
        self,
        event_type: str,
        customer_name: str,
        customer_phone: str,
        total_amount: float,
        soundbox_announcement: str,
        settled_khata_amount: float = 0.0,
        generate_audio: bool = True
    ) -> Dict[str, Any]:
        """Broadcasts a live event to all connected clients and generates TTS audio."""
        audio_url = ""
        if generate_audio:
            try:
                audio_url = await voice_service.synthesize_speech(soundbox_announcement)
            except Exception as e:
                print(f"TTS synthesis warning in broadcaster: {e}")
                audio_url = ""

        event = {
            "event_id": f"evt_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}_{len(self._history)+1}",
            "event_type": event_type,
            "customer_name": customer_name,
            "customer_phone": customer_phone,
            "total_amount": float(total_amount),
            "settled_khata_amount": float(settled_khata_amount),
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "soundbox_announcement": soundbox_announcement,
            "audio_url": audio_url,
            "is_soundbox_verified": True
        }

        # Store in rolling buffer
        self._history.insert(0, event)
        if len(self._history) > self._max_history:
            self._history.pop()

        # Push to all active SSE queues
        disconnected = []
        for queue in self._subscribers:
            try:
                queue.put_nowait(event)
            except Exception:
                disconnected.append(queue)

        for q in disconnected:
            if q in self._subscribers:
                self._subscribers.remove(q)

        return event

    async def subscribe(self) -> AsyncGenerator[str, None]:
        """Generator for Server-Sent Events (SSE) streaming."""
        queue: asyncio.Queue = asyncio.Queue()
        self._subscribers.append(queue)
        try:
            # Yield initial connection confirmation
            initial_payload = json.dumps({"status": "CONNECTED", "service": "Paytm VyapaarAI Soundbox Event Stream"})
            yield f"data: {initial_payload}\n\n"

            while True:
                event = await queue.get()
                yield f"data: {json.dumps(event)}\n\n"
        except (asyncio.CancelledError, GeneratorExit):
            pass
        finally:
            if queue in self._subscribers:
                self._subscribers.remove(queue)

    def get_recent_events(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Returns the most recent events."""
        return self._history[:limit]

event_broadcaster = SoundboxEventBroadcaster()
