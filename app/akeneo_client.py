# Akeneo references: https://api.akeneo.com/api-reference.html

import httpx
from app.config import settings

class AkeneoClient:
    def __init__(self) -> None:
        self.base_url = settings.akeneo_url.rstrip("/")

    async def ping(self) -> dict:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{self.base_url}/api/rest/v1")
            return {
                "status_code": response.status_code,
                "ok": response.is_success,
            }
