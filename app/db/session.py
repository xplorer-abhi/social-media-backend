from psycopg2 import pool
from app.core.config import settings

connection_pool = pool.SimpleConnectionPool(
    minconn=1,
    maxconn=10,
    dbname=settings.DATABASE_NAME,
    user=settings.DATABASE_USER,
    password=settings.DATABASE_PASSWORD,
    host=settings.DATABASE_HOST,
    port=settings.DATABASE_PORT,
)

def get_session():
    return connection_pool.getconn()

def release_session(conn):
    connection_pool.putconn(conn)
