from typing import Any

from app.db.connection import get_connection


def execute_write(query: str, params: tuple[Any, ...] | None = None) -> None:
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(query, params)
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def execute_returning_one(
    query: str,
    params: tuple[Any, ...] | None = None,
) -> tuple[Any, ...] | None:
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(query, params)
            row = cursor.fetchone()
        connection.commit()
        return row
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def fetch_one(query: str, params: tuple[Any, ...] | None = None) -> tuple[Any, ...] | None:
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchone()
    finally:
        connection.close()


def fetch_all(query: str, params: tuple[Any, ...] | None = None) -> list[tuple[Any, ...]]:
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchall()
    finally:
        connection.close()


def ensure_uuid_extension() -> None:
    """Enable pgcrypto so gen_random_uuid() is available for UUID primary keys."""
    execute_write("CREATE EXTENSION IF NOT EXISTS pgcrypto;")


def create_all_tables() -> None:
    """Create all project tables in dependency-safe order."""
    from app.models.comment_model import create_comments_table
    from app.models.follow_model import create_follows_table
    from app.models.like_model import create_likes_table
    from app.models.notification_model import create_notifications_table
    from app.models.post_model import create_posts_table
    from app.models.refresh_token_model import create_refresh_tokens_table
    from app.models.user_model import create_users_table

    ensure_uuid_extension()
    create_users_table()
    create_posts_table()
    create_comments_table()
    create_likes_table()
    create_follows_table()
    create_notifications_table()
    create_refresh_tokens_table()