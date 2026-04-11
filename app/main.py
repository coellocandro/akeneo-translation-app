# Akeneo sample apps: https://github.com/akeneo/sample-apps/tree/main
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI
from app.akeneo_client import AkeneoClient
from app.libretranslate_client import LibreTranslateClient

app = FastAPI()

@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}

@app.get("/akeneo-test")
async def akeneo_test() -> dict:
    client = AkeneoClient()
    return await client.ping()

@app.get("/products-test")
async def products_test() -> dict:
    client = AkeneoClient()
    return await client.get_products()

@app.get("/auth-test")
async def auth_test() -> dict:
    client = AkeneoClient()
    return await client.get_access_token()

@app.get("/products-auth-test")
async def products_auth_test() -> dict:
    client = AkeneoClient()
    return await client.get_products_authenticated()

@app.get("/product/{identifier}")
async def get_product(identifier: str) -> dict:
    client = AkeneoClient()
    return await client.get_product(identifier)

@app.get("/translate-test")
async def translate_test() -> dict:
    client = LibreTranslateClient()
    return await client.translate_text("Hello world!", "en", "es")