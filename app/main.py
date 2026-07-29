from fastapi import FastAPI
from fastapi import HTTPException

from app.db.connection import test_db_connection

app = FastAPI()


@app.get("/")
def home():
    return {"message": "Social Media Backend Running"}


@app.get("/health/db")
def db_health_check():
    is_connected, message = test_db_connection()
    if not is_connected:
        raise HTTPException(status_code=503, detail=message)
    return {"status": "ok", "message": message}