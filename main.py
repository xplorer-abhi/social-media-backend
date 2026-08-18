from fastapi import FastAPI
from fastapi import HTTPException

from app.db.connection import test_db_connection
from app.services.auth import router as auth_router
from app.services.comments import router as comments_router
from app.services.follows import router as follows_router
from app.services.likes import router as likes_router
from app.services.posts import router as posts_router

app = FastAPI()
app.include_router(auth_router, prefix="/api/v1")
app.include_router(comments_router, prefix="/api/v1")
app.include_router(follows_router, prefix="/api/v1")
app.include_router(likes_router, prefix="/api/v1")
app.include_router(posts_router, prefix="/api/v1")


@app.get("/")
def home():
    return {"message": "Social Media Backend Running"}


@app.get("/health/db")
def db_health_check():
    is_connected, message = test_db_connection()
    if not is_connected:
        raise HTTPException(status_code=503, detail=message)
    return {"status": "ok", "message": message}