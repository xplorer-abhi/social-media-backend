from typing import Any

from app.models.base import execute_returning_one, execute_write, fetch_all, fetch_one


def create_comments_table() -> None:
	query = """
	CREATE TABLE IF NOT EXISTS comments (
		id BIGSERIAL PRIMARY KEY,
		post_id BIGINT NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
		user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
		content TEXT NOT NULL CHECK (LENGTH(BTRIM(content)) > 0),
		created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
	);
	"""
	execute_write(query)


def insert_comment(post_id: int, user_id: int, content: str) -> int:
	query = """
	INSERT INTO comments (post_id, user_id, content)
	VALUES (%s, %s, %s)
	RETURNING id;
	"""
	row = execute_returning_one(query, (post_id, user_id, content))
	if row is None:
		raise RuntimeError("Failed to create comment")
	return int(row[0])


def fetch_comment_by_id(comment_id: int) -> tuple[Any, ...] | None:
	query = """
	SELECT id, post_id, user_id, content, created_at
	FROM comments
	WHERE id = %s;
	"""
	return fetch_one(query, (comment_id,))


def fetch_comments_by_post(post_id: int) -> list[tuple[Any, ...]]:
	query = """
	SELECT id, post_id, user_id, content, created_at
	FROM comments
	WHERE post_id = %s
	ORDER BY created_at ASC;
	"""
	return fetch_all(query, (post_id,))


def update_comment(comment_id: int, content: str) -> None:
	query = """
	UPDATE comments
	SET content = %s
	WHERE id = %s;
	"""
	execute_write(query, (content, comment_id))


def delete_comment(comment_id: int) -> None:
	query = "DELETE FROM comments WHERE id = %s;"
	execute_write(query, (comment_id,))
