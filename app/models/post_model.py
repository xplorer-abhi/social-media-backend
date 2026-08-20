from typing import Any

from app.models.base import execute_returning_one, execute_write, fetch_all, fetch_one


def create_posts_table() -> None:
    query = """
    CREATE TABLE IF NOT EXISTS posts (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        content TEXT NOT NULL CHECK (LENGTH(BTRIM(content)) > 0),
        image_url TEXT,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );
    """
    execute_write(query)


def insert_post(user_id: str, content: str, image_url: str | None = None) -> str:
    query = """
    INSERT INTO posts (user_id, content, image_url)
    VALUES (%s, %s, %s)
    RETURNING id;
    """
    row = execute_returning_one(query, (user_id, content, image_url))
    if row is None:
        raise RuntimeError("Failed to create post")
    return str(row[0])


def fetch_post_by_id(post_id: str) -> tuple[Any, ...] | None:
    query = """
    SELECT id, user_id, content, image_url, created_at, updated_at
    FROM posts
    WHERE id = %s;
    """
    return fetch_one(query, (post_id,))


def fetch_posts_by_user(user_id: str) -> list[tuple[Any, ...]]:
    query = """
    SELECT id, user_id, content, image_url, created_at, updated_at
    FROM posts
    WHERE user_id = %s
    ORDER BY created_at DESC;
    """
    return fetch_all(query, (user_id,))


def update_post(post_id: str, content: str, image_url: str | None = None) -> None:
    query = """
    UPDATE posts
    SET content = %s,
        image_url = %s,
        updated_at = NOW()
    WHERE id = %s;
    """
    execute_write(query, (content, image_url, post_id))


def delete_post(post_id: str) -> None:
    query = "DELETE FROM posts WHERE id = %s;"
    execute_write(query, (post_id,))


def count_posts_by_user(user_id: str) -> int:
    query = "SELECT COUNT(*) FROM posts WHERE user_id = %s;"
    row = fetch_one(query, (user_id,))
    return int(row[0]) if row is not None else 0
