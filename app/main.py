# Akeneo sample app: https://github.com/akeneo/sample-apps/tree/main
from fastapi import FastAPI
from dotenv import load_dotenv
from app.akeneo_client import AkeneoClient

load_dotenv()
app = FastAPI()

@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}

@app.get("/akeneo-test")
async def akeneo_test() -> dict:
    client = AkeneoClient()
    return await client.ping()
