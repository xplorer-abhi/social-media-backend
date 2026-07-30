from datetime import datetime
from typing import Any

from app.models.base import execute_returning_one, execute_write, fetch_all, fetch_one


def create_refresh_tokens_table() -> None:
    query = """
    CREATE TABLE IF NOT EXISTS refresh_tokens (
        id BIGSERIAL PRIMARY KEY,
        user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        token TEXT NOT NULL UNIQUE,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        expires_at TIMESTAMPTZ NOT NULL
    );
    """
    execute_write(query)


def insert_refresh_token(user_id: int, token: str, expires_at: datetime) -> int:
    query = """
    INSERT INTO refresh_tokens (user_id, token, expires_at)
    VALUES (%s, %s, %s)
    RETURNING id;
    """
    row = execute_returning_one(query, (user_id, token, expires_at))
    if row is None:
        raise RuntimeError("Failed to create refresh token")
    return int(row[0])


def fetch_refresh_token(token: str) -> tuple[Any, ...] | None:
    query = """
    SELECT id, user_id, token, created_at, expires_at
    FROM refresh_tokens
    WHERE token = %s;
    """
    return fetch_one(query, (token,))


def fetch_refresh_tokens_by_user(user_id: int) -> list[tuple[Any, ...]]:
    query = """
    SELECT id, user_id, token, created_at, expires_at
    FROM refresh_tokens
    WHERE user_id = %s
    ORDER BY created_at DESC;
    """
    return fetch_all(query, (user_id,))


def delete_refresh_token(token: str) -> None:
    query = "DELETE FROM refresh_tokens WHERE token = %s;"
    execute_write(query, (token,))


def delete_expired_refresh_tokens() -> None:
    query = "DELETE FROM refresh_tokens WHERE expires_at <= NOW();"
    execute_write(query)