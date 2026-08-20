from datetime import datetime
from typing import Any

from app.models.base import execute_returning_one, execute_write, fetch_all, fetch_one


def create_refresh_tokens_table() -> None:
    query = """
    CREATE TABLE IF NOT EXISTS refresh_tokens (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        token_hash TEXT NOT NULL UNIQUE,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        expires_at TIMESTAMPTZ NOT NULL
    );
    """
    execute_write(query)


def insert_refresh_token(user_id: str, token_hash: str, expires_at: datetime) -> str:
    query = """
    INSERT INTO refresh_tokens (user_id, token_hash, expires_at)
    VALUES (%s, %s, %s)
    RETURNING id;
    """
    row = execute_returning_one(query, (user_id, token_hash, expires_at))
    if row is None:
        raise RuntimeError("Failed to create refresh token")
    return str(row[0])


def fetch_refresh_token(token_hash: str) -> tuple[Any, ...] | None:
    query = """
    SELECT id, user_id, token_hash, created_at, expires_at
    FROM refresh_tokens
    WHERE token_hash = %s;
    """
    return fetch_one(query, (token_hash,))


def fetch_refresh_tokens_by_user(user_id: str) -> list[tuple[Any, ...]]:
    query = """
    SELECT id, user_id, token_hash, created_at, expires_at
    FROM refresh_tokens
    WHERE user_id = %s
    ORDER BY created_at DESC;
    """
    return fetch_all(query, (user_id,))


def delete_refresh_token(token_hash: str) -> None:
    query = "DELETE FROM refresh_tokens WHERE token_hash = %s;"
    execute_write(query, (token_hash,))


def delete_expired_refresh_tokens() -> None:
    query = "DELETE FROM refresh_tokens WHERE expires_at <= NOW();"
    execute_write(query)