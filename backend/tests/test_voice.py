import pytest
import io
import httpx
import pytest_asyncio
from app.main import app
from app.init_db import init_db

@pytest.mark.asyncio
async def test_voice_copilot_pipeline():
    await init_db()
    # Mock audio bytes
    fake_audio = io.BytesIO(b"RIFF....WAVEfmt ....data....")
    files = {"audio_file": ("test_voice.wav", fake_audio, "audio/wav")}
    data = {"merchant_id": "sharma-kirana-001"}

    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.post("/api/v1/copilot/voice-query", data=data, files=files)

    assert res.status_code == 200
    res_data = res.json()
    assert res_data["status"] == "SUCCESS"
    assert "transcription" in res_data
    assert "voice_reply_transcript" in res_data
    assert "voice_reply_audio_url" in res_data
    assert res_data["data_payload"]["today_total_sales"] >= 9420.0
    assert res_data["data_payload"]["total_khata_pending"] == 2250.0
