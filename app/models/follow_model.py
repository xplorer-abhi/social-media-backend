from typing import Any

from app.models.base import execute_returning_one, execute_write, fetch_all, fetch_one


def create_follows_table() -> None:
	query = """
	CREATE TABLE IF NOT EXISTS follows (
		id BIGSERIAL PRIMARY KEY,
		follower_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
		following_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
		created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
		CONSTRAINT uq_follows_pair UNIQUE (follower_id, following_id),
		CONSTRAINT chk_no_self_follow CHECK (follower_id <> following_id)
	);
	"""
	execute_write(query)


def add_follow(follower_id: int, following_id: int) -> int:
	query = """
	INSERT INTO follows (follower_id, following_id)
	VALUES (%s, %s)
	RETURNING id;
	"""
	row = execute_returning_one(query, (follower_id, following_id))
	if row is None:
		raise RuntimeError("Failed to create follow")
	return int(row[0])


def remove_follow(follower_id: int, following_id: int) -> None:
	query = "DELETE FROM follows WHERE follower_id = %s AND following_id = %s;"
	execute_write(query, (follower_id, following_id))


def fetch_following(user_id: int) -> list[tuple[Any, ...]]:
	query = """
	SELECT id, follower_id, following_id, created_at
	FROM follows
	WHERE follower_id = %s
	ORDER BY created_at DESC;
	"""
	return fetch_all(query, (user_id,))


def fetch_followers(user_id: int) -> list[tuple[Any, ...]]:
	query = """
	SELECT id, follower_id, following_id, created_at
	FROM follows
	WHERE following_id = %s
	ORDER BY created_at DESC;
	"""
	return fetch_all(query, (user_id,))


def is_following(follower_id: int, following_id: int) -> bool:
	query = """
	SELECT 1
	FROM follows
	WHERE follower_id = %s AND following_id = %s;
	"""
	row = fetch_one(query, (follower_id, following_id))
	return row is not None
