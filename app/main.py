from fastapi import FastAPI
from dotenv import load_dotenv
from app.config import settings

load_dotenv()
app = FastAPI()

@app.get("/test")
def test() -> dict[str, str]:
	return {"status": "success"}
