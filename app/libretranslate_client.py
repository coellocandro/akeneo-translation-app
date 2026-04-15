# LibreTranslate doc: https://libretranslate.com/docs/
import httpx
from app.config import settings

class LibreTranslateClient:
    def __init__(self) -> None:
        self.base_url = settings.libretranslate_url.rstrip("/")

    async def translate_text(self, text: str, source: str, target: str) -> dict:
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.post(
                f"{self.base_url}/translate",
                json={
                    "q": text,
                    "source": source,
                    "target": target,
                    "format": "text",
                },
            )
            response.raise_for_status()
            return response.json()

            # return {
            #     "status_code": response.status_code,
            #     "ok": response.is_success,
            #     "data": response.json(),
            # }