import psycopg2
from app.core.config import settings


def get_connection():
    return psycopg2.connect(
        dbname=settings.DATABASE_NAME,
        user=settings.DATABASE_USER,
        password=settings.DATABASE_PASSWORD,
        host=settings.DATABASE_HOST,
        port=settings.DATABASE_PORT,
        connect_timeout=5,
    )


def test_db_connection() -> tuple[bool, str]:
    connection = None
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1;")
            cursor.fetchone()
        return True, "Database connection successful"
    except Exception as exc:
        return False, f"Database connection failed: {exc}"
    finally:
        if connection is not None:
            connection.close()