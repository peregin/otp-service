import os
import psycopg2
from typing import Optional, Tuple

# Database configuration
DB_NAME = os.getenv("DB_NAME", "otp")
DB_USER = os.getenv("DB_USER", "otp")
DB_PASSWORD = os.getenv("DB_PASSWORD", "otp")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5490")
DB_PARAMS = f"dbname={DB_NAME} user={DB_USER} password={DB_PASSWORD} host={DB_HOST} port={DB_PORT}"

def init_db():
    """Initialize the database and create required tables"""
    with psycopg2.connect(DB_PARAMS) as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                            id SERIAL PRIMARY KEY,
                            username TEXT UNIQUE,
                            secret TEXT)''')
        conn.commit()

def register_user(username: str, secret: str) -> Optional[str]:
    """
    Register a new user in the database
    Returns None on success, error message on failure
    """
    try:
        with psycopg2.connect(DB_PARAMS) as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO users (username, secret) VALUES (%s, %s)",
                    (username, secret)
                )
                conn.commit()
        return None
    except psycopg2.IntegrityError:
        return "Username already exists"


def get_user_secret(username: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Get user's secret from database
    Returns: Tuple[secret, error_message]
    If successful: (secret, None)
    If failed: (None, error_message)
    """
    try:
        with psycopg2.connect(DB_PARAMS) as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT secret FROM users WHERE username = %s", (username,))
                row = cursor.fetchone()

                if not row:
                    return None, "User not found"
                return row[0], None
    except psycopg2.Error as e:
        return None, f"Database error: {str(e)}"