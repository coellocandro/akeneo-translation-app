# Akeneo references: https://api.akeneo.com/api-reference.html
import base64, httpx
from app.config import settings

class AkeneoClient:
    def __init__(self) -> None:
        self.base_url = settings.akeneo_url.rstrip("/")
        self._access_token: str | None = None
        
    def _basic_auth_header(self) -> dict[str, str]:
        credentials = f"{settings.akeneo_client_id}:{settings.akeneo_client_secret}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        return {
            "Authorization": f"Basic {encoded_credentials}",
            "Content-Type": "application/json",
        }
    
    async def _bearer_headers(self) -> dict[str, str]:
        if not self._access_token:
            self._access_token = await self.fetch_access_token()
        return {"Authorization": f"Bearer {self._access_token}"}
    
    async def fetch_access_token(self) -> str:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{self.base_url}/api/oauth/v1/token",
                headers=self._basic_auth_header(),
                json={
                    "grant_type": "password",
                    "username": settings.akeneo_username,
                    "password": settings.akeneo_password,
                },
            )
            response.raise_for_status()
            return response.json()["access_token"]
       
    async def get_pim_content(self, identifier: str) -> dict:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{self.base_url}/api/rest/v1/products/{identifier}",
                headers=await self._bearer_headers(),
            )
            response.raise_for_status()
            data = response.json()
            return {
                "identifier": data["identifier"],
                "values": data.get("values", {}),
            }
        
    async def patch_translation_to_pim(self, identifier: str, values: dict) -> dict:
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.patch(
                f"{self.base_url}/api/rest/v1/products/{identifier}",
                headers={
                    **await self._bearer_headers(),
                    "Content-Type": "application/json",
                },
                json={"values": values},
            )
            return {
                "status_code": response.status_code,
                "ok": response.is_success,
                "body": response.text,
            }