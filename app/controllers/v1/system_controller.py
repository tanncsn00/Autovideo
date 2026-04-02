import platform
import sys

from app.controllers.v1.base import new_router
from app.config import config
from app.utils import utils

router = new_router()


@router.get("/system/info", summary="Get system information")
def get_system_info():
    info = {
        "version": config.project_version,
        "python_version": sys.version,
        "platform": platform.system(),
        "platform_version": platform.version(),
        "machine": platform.machine(),
        "mode": config.get_mode(),
    }
    return utils.get_response(200, info)


@router.get("/ping", summary="Health check")
def ping():
    return utils.get_response(200, {"message": "pong"})


@router.get("/voices", summary="List all available TTS voices")
def list_voices(language: str = None):
    import asyncio
    import edge_tts

    voices = asyncio.run(edge_tts.list_voices())
    result = []
    for v in voices:
        if language and not v["Locale"].startswith(language):
            continue
        result.append({
            "name": v["ShortName"],
            "display_name": v["FriendlyName"],
            "gender": v["Gender"],
            "locale": v["Locale"],
            "language": v["Locale"].split("-")[0],
            "provider": "edge-tts",
        })

    # Add FPT.AI Vietnamese voices
    fpt_voices = [
        {"name": "fpt-banmai", "display_name": "Ban Mai (FPT.AI) - Nữ miền Bắc", "gender": "Female", "locale": "vi-VN", "language": "vi", "provider": "fpt-ai"},
        {"name": "fpt-lannhi", "display_name": "Lan Nhi (FPT.AI) - Nữ miền Nam", "gender": "Female", "locale": "vi-VN", "language": "vi", "provider": "fpt-ai"},
        {"name": "fpt-leminh", "display_name": "Lê Minh (FPT.AI) - Nam miền Bắc", "gender": "Male", "locale": "vi-VN", "language": "vi", "provider": "fpt-ai"},
        {"name": "fpt-myan", "display_name": "Mỹ An (FPT.AI) - Nữ miền Trung", "gender": "Female", "locale": "vi-VN", "language": "vi", "provider": "fpt-ai"},
        {"name": "fpt-thuminh", "display_name": "Thu Minh (FPT.AI) - Nữ miền Bắc", "gender": "Female", "locale": "vi-VN", "language": "vi", "provider": "fpt-ai"},
        {"name": "fpt-giahuy", "display_name": "Gia Huy (FPT.AI) - Nam miền Nam", "gender": "Male", "locale": "vi-VN", "language": "vi", "provider": "fpt-ai"},
        {"name": "fpt-ngoclam", "display_name": "Ngọc Lam (FPT.AI) - Nữ miền Nam", "gender": "Female", "locale": "vi-VN", "language": "vi", "provider": "fpt-ai"},
    ]
    for fv in fpt_voices:
        if language and not fv["locale"].startswith(language):
            continue
        result.append(fv)

    # Add VBee Vietnamese voices
    vbee_voices = [
        {"name": "vbee-hn_female_ngochuyen_news_48k-1", "display_name": "Ngọc Huyền (VBee) - Nữ đọc truyện", "gender": "Female", "locale": "vi-VN", "language": "vi", "provider": "vbee"},
        {"name": "vbee-hn_male_manhdung_news_48k-1", "display_name": "Mạnh Dũng (VBee) - Nam đọc tin", "gender": "Male", "locale": "vi-VN", "language": "vi", "provider": "vbee"},
    ]
    for vv in vbee_voices:
        if language and not vv["locale"].startswith(language):
            continue
        result.append(vv)

    return utils.get_response(200, result)


@router.post("/voices/preview", summary="Preview a voice (generate short audio)")
async def preview_voice(body: dict):
    import tempfile
    import os
    from fastapi.responses import FileResponse

    voice_name = body.get("voice", "en-US-AriaNeural")
    text = body.get("text", "Hello, this is a preview of my voice. How does it sound?")

    temp_file = os.path.join(tempfile.gettempdir(), f"preview_{voice_name}.mp3")

    if voice_name.startswith("fpt-"):
        # FPT.AI voice preview
        import requests as _req
        from app.config.config import get_api_key
        fpt_key = get_api_key("fpt_ai_api_key")
        if not fpt_key:
            return utils.get_response(400, message="FPT.AI API key not set")
        fpt_voice = voice_name.replace("fpt-", "")
        resp = _req.post(
            "https://api.fpt.ai/hmi/tts/v5",
            headers={"api-key": fpt_key, "voice": fpt_voice, "speed": "0"},
            data=text.encode("utf-8"),
        )
        if resp.status_code == 200:
            data = resp.json()
            audio_url = data.get("async")
            if audio_url:
                import time
                time.sleep(2)  # Wait for FPT to process
                audio_resp = _req.get(audio_url)
                if audio_resp.status_code == 200:
                    with open(temp_file, "wb") as f:
                        f.write(audio_resp.content)
                    return FileResponse(temp_file, media_type="audio/mpeg")
        return utils.get_response(500, message="FPT.AI preview failed")

    elif voice_name.startswith("vbee-"):
        return utils.get_response(400, message="VBee preview not supported yet")

    else:
        # Edge TTS
        communicate = edge_tts.Communicate(text=text, voice=voice_name)
        await communicate.save(temp_file)
        return FileResponse(temp_file, media_type="audio/mpeg", filename=f"preview_{voice_name}.mp3")


import edge_tts
import os as _os
from fastapi.responses import FileResponse as _FileResponse


@router.get("/musics/play/{filename}", summary="Stream a BGM file for preview")
def play_bgm(filename: str):
    from app.utils import utils
    song_dir = utils.song_dir()
    file_path = _os.path.join(song_dir, filename)
    if not _os.path.exists(file_path):
        return utils.get_response(404, message=f"File not found: {filename}")
    return _FileResponse(file_path, media_type="audio/mpeg", filename=filename)
