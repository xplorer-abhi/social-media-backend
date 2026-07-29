from typing import Any

from app.models.base import execute_write, fetch_all

def create_notifications_table() -> None:
    query = """
    CREATE TABLE IF NOT EXISTS notifications (
        id BIGSERIAL PRIMARY KEY,
        user_id BIGINT NOT NULL,
        type VARCHAR(50) NOT NULL,         -- e.g., 'like', 'comment', 'follow'
        message TEXT NOT NULL,             -- human-readable message
        is_read BOOLEAN NOT NULL DEFAULT FALSE,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    );
    """
    execute_write(query)


def insert_notification(user_id: int, notif_type: str, message: str) -> None:
    query = """
    INSERT INTO notifications (user_id, type, message)
    VALUES (%s, %s, %s);
    """
    execute_write(query, (user_id, notif_type, message))


def fetch_unread_notifications(user_id: int) -> list[tuple[Any, ...]]:
    query = """
    SELECT id, type, message, created_at
    FROM notifications
    WHERE user_id = %s AND is_read = FALSE
    ORDER BY created_at DESC;
    """
    return fetch_all(query, (user_id,))


def mark_notification_as_read(notification_id: int) -> None:
    query = "UPDATE notifications SET is_read = TRUE WHERE id = %s;"
    execute_write(query, (notification_id,))
