from typing import Any

from app.models.base import execute_returning_one, execute_write, fetch_all, fetch_one


def create_comments_table() -> None:
	query = """
	CREATE TABLE IF NOT EXISTS comments (
		id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
		post_id UUID NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
		user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
		content TEXT NOT NULL CHECK (LENGTH(BTRIM(content)) > 0),
		created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
	);
	"""
	execute_write(query)


def insert_comment(post_id: str, user_id: str, content: str) -> str:
	query = """
	INSERT INTO comments (post_id, user_id, content)
	VALUES (%s, %s, %s)
	RETURNING id;
	"""
	row = execute_returning_one(query, (post_id, user_id, content))
	if row is None:
		raise RuntimeError("Failed to create comment")
	return str(row[0])


def fetch_comment_by_id(comment_id: str) -> tuple[Any, ...] | None:
	query = """
	SELECT id, post_id, user_id, content, created_at
	FROM comments
	WHERE id = %s;
	"""
	return fetch_one(query, (comment_id,))


def fetch_comments_by_post(post_id: str) -> list[tuple[Any, ...]]:
	query = """
	SELECT id, post_id, user_id, content, created_at
	FROM comments
	WHERE post_id = %s
	ORDER BY created_at ASC;
	"""
	return fetch_all(query, (post_id,))


def update_comment(comment_id: str, content: str) -> None:
	query = """
	UPDATE comments
	SET content = %s
	WHERE id = %s;
	"""
	execute_write(query, (content, comment_id))


def delete_comment(comment_id: str) -> None:
	query = "DELETE FROM comments WHERE id = %s;"
	execute_write(query, (comment_id,))
