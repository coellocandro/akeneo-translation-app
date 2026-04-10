from fastapi import FastAPI

app = FastAPI()

@app.get("/test")
def test() -> dict[str, str]:
	return {"status": "success"}