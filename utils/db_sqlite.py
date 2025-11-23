import sqlite3
from utils.config import Config


def get_db():
    conn = sqlite3.connect(Config.DB_PATH)

    # returns rows as dict-like objects
    conn.row_factory = sqlite3.Row
    return conn


def init_sqlite_db():
    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        """ 
            CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL,
            is_active BOOLEAN NOT NULL DEFAULT FALSE
        		)
    		"""
    )

    # Unique email index for email-based login
    cur.execute(
        """ 
            CREATE UNIQUE INDEX IF NOT EXISTS idx_users_email_unique ON users(email)
    		"""
    )

    conn.commit()
    conn.close()
