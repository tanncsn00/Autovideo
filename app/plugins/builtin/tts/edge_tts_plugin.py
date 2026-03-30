import edge_tts
from app.plugins.base import TTSPlugin, PluginMeta
from app.plugins.utils import run_async


class EdgeTTSPlugin(TTSPlugin):

    def get_meta(self) -> PluginMeta:
        return PluginMeta(
            name="edge-tts",
            display_name="Microsoft Edge TTS",
            version="1.0.0",
            description="Free Azure Edge TTS with 400+ multilingual voices",
            author="MoneyPrinterTurbo",
            plugin_type="tts",
            builtin=True,
        )

    def validate_config(self, config: dict) -> bool:
        return True  # No config needed

    def is_available(self) -> bool:
        return True  # Always available (free service)

    async def synthesize(self, text, voice, rate=1.0, output_path=""):
        rate_str = f"+{int((rate - 1) * 100)}%" if rate >= 1 else f"{int((rate - 1) * 100)}%"
        communicate = edge_tts.Communicate(text=text, voice=voice, rate=rate_str)
        sub_maker = edge_tts.SubMaker()
        with open(output_path, "wb") as f:
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    f.write(chunk["data"])
                elif chunk["type"] == "WordBoundary":
                    sub_maker.feed(chunk)
        return output_path, sub_maker

    def get_voices(self) -> list[dict]:
        voices = run_async(edge_tts.list_voices())
        return [
            {
                "id": v["ShortName"],
                "name": v["FriendlyName"],
                "language": v["Locale"],
                "gender": v["Gender"],
            }
            for v in voices
        ]
