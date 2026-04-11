# Akeneo references: https://api.akeneo.com/api-reference.html
import httpx
import base64
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

    async def get_access_token(self) -> dict:
        credentials = f"{settings.akeneo_client_id}:{settings.akeneo_client_secret}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{self.base_url}/api/oauth/v1/token",
                headers={
                    "Authorization": f"Basic {encoded_credentials}",
                    "Content-Type": "application/json",
                },
                json={
                    "grant_type": "password",
                    "username": settings.akeneo_username,
                    "password": settings.akeneo_password,
                },
            )
            return {
                "status_code": response.status_code,
                "ok": response.is_success,
                "body": response.text[:500],
            }
        
    async def fetch_access_token(self) -> str:
        credentials = f"{settings.akeneo_client_id}:{settings.akeneo_client_secret}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{self.base_url}/api/oauth/v1/token",
                headers={
                    "Authorization": f"Basic {encoded_credentials}",
                    "Content-Type": "application/json",
                },
                json={
                    "grant_type": "password",
                    "username": settings.akeneo_username,
                    "password": settings.akeneo_password,
                },
            )
            response.raise_for_status()
            data = response.json()
            return data["access_token"]

    async def get_products_authenticated(self) -> dict:
        token = await self.fetch_access_token()

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{self.base_url}/api/rest/v1/products",
                headers={"Authorization": f"Bearer {token}"},
            )
            return {
                "status_code": response.status_code,
                "ok": response.is_success,
                "body": response.text[:1000],
            }

    # async def get_access_token(self) -> dict:
    #     async with httpx.AsyncClient(timeout=10.0) as client:
    #         response = await client.post(
    #             f"{self.base_url}/api/oauth/v1/token",
    #             json={
    #                 "grant_type": "password",
    #                 "username": settings.akeneo_username,
    #                 "password": settings.akeneo_password,
    #             },
    #         )
    #         return {
    #             "status_code": response.status_code,
    #             "ok": response.is_success,
    #             "body": response.text[:500],
    #         }