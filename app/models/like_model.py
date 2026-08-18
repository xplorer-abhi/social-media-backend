from typing import Any

from app.models.base import execute_returning_one, execute_write, fetch_all, fetch_one


def create_likes_table() -> None:
	query = """
	CREATE TABLE IF NOT EXISTS likes (
		id BIGSERIAL PRIMARY KEY,
		post_id BIGINT NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
		user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
		created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
		CONSTRAINT uq_likes_post_user UNIQUE (post_id, user_id)
	);
	"""
	execute_write(query)


def add_like(post_id: int, user_id: int) -> int:
	query = """
	INSERT INTO likes (post_id, user_id)
	VALUES (%s, %s)
	RETURNING id;
	"""
	row = execute_returning_one(query, (post_id, user_id))
	if row is None:
		raise RuntimeError("Failed to add like")
	return int(row[0])


def fetch_like(post_id: int, user_id: int) -> tuple[Any, ...] | None:
	query = """
	SELECT id, post_id, user_id, created_at
	FROM likes
	WHERE post_id = %s AND user_id = %s;
	"""
	return fetch_one(query, (post_id, user_id))


def remove_like(post_id: int, user_id: int) -> None:
	query = "DELETE FROM likes WHERE post_id = %s AND user_id = %s;"
	execute_write(query, (post_id, user_id))


def fetch_likes_by_post(post_id: int) -> list[tuple[Any, ...]]:
	query = """
	SELECT id, post_id, user_id, created_at
	FROM likes
	WHERE post_id = %s
	ORDER BY created_at DESC;
	"""
	return fetch_all(query, (post_id,))


def count_likes_by_post(post_id: int) -> int:
	query = "SELECT COUNT(*) FROM likes WHERE post_id = %s;"
	row = fetch_one(query, (post_id,))
	return int(row[0]) if row is not None else 0
