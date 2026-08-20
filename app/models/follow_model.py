from typing import Any

from app.models.base import execute_returning_one, execute_write, fetch_all, fetch_one


def create_follows_table() -> None:
	query = """
	CREATE TABLE IF NOT EXISTS follows (
		id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
		follower_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
		following_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
		created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
		CONSTRAINT uq_follows_pair UNIQUE (follower_id, following_id),
		CONSTRAINT chk_no_self_follow CHECK (follower_id <> following_id)
	);
	"""
	execute_write(query)


def add_follow(follower_id: str, following_id: str) -> str:
	query = """
	INSERT INTO follows (follower_id, following_id)
	VALUES (%s, %s)
	RETURNING id;
	"""
	row = execute_returning_one(query, (follower_id, following_id))
	if row is None:
		raise RuntimeError("Failed to create follow")
	return str(row[0])


def remove_follow(follower_id: str, following_id: str) -> None:
	query = "DELETE FROM follows WHERE follower_id = %s AND following_id = %s;"
	execute_write(query, (follower_id, following_id))


def fetch_following(user_id: str) -> list[tuple[Any, ...]]:
	query = """
	SELECT id, follower_id, following_id, created_at
	FROM follows
	WHERE follower_id = %s
	ORDER BY created_at DESC;
	"""
	return fetch_all(query, (user_id,))


def fetch_followers(user_id: str) -> list[tuple[Any, ...]]:
	query = """
	SELECT id, follower_id, following_id, created_at
	FROM follows
	WHERE following_id = %s
	ORDER BY created_at DESC;
	"""
	return fetch_all(query, (user_id,))


def is_following(follower_id: str, following_id: str) -> bool:
	query = """
	SELECT 1
	FROM follows
	WHERE follower_id = %s AND following_id = %s;
	"""
	row = fetch_one(query, (follower_id, following_id))
	return row is not None


def count_followers(user_id: str) -> int:
	query = "SELECT COUNT(*) FROM follows WHERE following_id = %s;"
	row = fetch_one(query, (user_id,))
	return int(row[0]) if row is not None else 0


def count_following(user_id: str) -> int:
	query = "SELECT COUNT(*) FROM follows WHERE follower_id = %s;"
	row = fetch_one(query, (user_id,))
	return int(row[0]) if row is not None else 0
