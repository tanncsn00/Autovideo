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
        })
    return utils.get_response(200, result)


@router.post("/voices/preview", summary="Preview a voice (generate short audio)")
async def preview_voice(body: dict):
    import asyncio
    import tempfile
    import os
    from fastapi.responses import FileResponse

    voice_name = body.get("voice", "en-US-AriaNeural")
    text = body.get("text", "Hello, this is a preview of my voice. How does it sound?")

    temp_file = os.path.join(tempfile.gettempdir(), f"preview_{voice_name}.mp3")
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
