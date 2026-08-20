from typing import Any

from app.models.base import execute_returning_one, execute_write, fetch_all, fetch_one


def create_users_table() -> None:
    query = """
    CREATE TABLE IF NOT EXISTS users (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        username VARCHAR(50) NOT NULL UNIQUE,
        email VARCHAR(255) NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        bio TEXT,
        profile_picture TEXT,
        is_active BOOLEAN NOT NULL DEFAULT TRUE,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );
    """
    execute_write(query)


def insert_user(username: str, email: str, password_hash: str) -> str:
    query = """
    INSERT INTO users (username, email, password_hash)
    VALUES (%s, %s, %s)
    RETURNING id;
    """
    row = execute_returning_one(query, (username, email, password_hash))
    if row is None:
        raise RuntimeError("Failed to create user")
    return str(row[0])


def fetch_user_by_id(user_id: str) -> tuple[Any, ...] | None:
    query = """
    SELECT id, username, email, bio, profile_picture, is_active, created_at, updated_at
    FROM users
    WHERE id = %s;
    """
    return fetch_one(query, (user_id,))


def fetch_user_by_email(email: str) -> tuple[Any, ...] | None:
    query = """
    SELECT id, username, email, password_hash, bio, profile_picture, is_active, created_at, updated_at
    FROM users
    WHERE email = %s;
    """
    return fetch_one(query, (email,))


def fetch_user_by_username(username: str) -> tuple[Any, ...] | None:
    query = """
    SELECT id, username, email, bio, profile_picture, is_active, created_at, updated_at
    FROM users
    WHERE username = %s;
    """
    return fetch_one(query, (username,))


def fetch_user_credentials_by_username(username: str) -> tuple[Any, ...] | None:
    query = """
    SELECT id, username, email, password_hash, bio, profile_picture, is_active, created_at, updated_at
    FROM users
    WHERE username = %s;
    """
    return fetch_one(query, (username,))


def fetch_all_users() -> list[tuple[Any, ...]]:
    query = """
    SELECT id, username, email, is_active, created_at, updated_at
    FROM users
    ORDER BY id ASC;
    """
    return fetch_all(query)


def search_users_by_username(search_term: str, limit: int = 20) -> list[tuple[Any, ...]]:
    query = """
    SELECT id, username, bio, profile_picture
    FROM users
    WHERE is_active = TRUE AND username ILIKE %s
    ORDER BY username ASC
    LIMIT %s;
    """
    return fetch_all(query, (f"%{search_term}%", limit))


def update_user_profile(
    user_id: str,
    username: str,
    bio: str | None,
    profile_picture: str | None,
    is_active: bool,
) -> None:
    query = """
    UPDATE users
    SET username = %s,
        bio = %s,
        profile_picture = %s,
        is_active = %s,
        updated_at = NOW()
    WHERE id = %s;
    """
    execute_write(query, (username, bio, profile_picture, is_active, user_id))


def delete_user(user_id: str) -> None:
    query = "DELETE FROM users WHERE id = %s;"
    execute_write(query, (user_id,))


def fetch_user_password_hash(user_id: str) -> str | None:
    query = "SELECT password_hash FROM users WHERE id = %s;"
    row = fetch_one(query, (user_id,))
    return row[0] if row is not None else None


def update_user_password(user_id: str, password_hash: str) -> None:
    query = """
    UPDATE users
    SET password_hash = %s,
        updated_at = NOW()
    WHERE id = %s;
    """
    execute_write(query, (password_hash, user_id))
