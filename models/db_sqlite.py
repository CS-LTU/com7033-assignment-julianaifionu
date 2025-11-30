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

    # Roles table
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS roles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT
        );
        """
    )

    # Users table
    cur.execute(
        """ 
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role_id INTEGER NOT NULL,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT,
            is_active BOOLEAN NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL,
            updated_at TEXT,
            FOREIGN KEY (role_id) REFERENCES roles(id)
        );
    		"""
    )

    # Index for fast username lookups
    cur.execute(
        """ 
            CREATE UNIQUE INDEX IF NOT EXISTS idx_users_username_unique ON users(username);
    		"""
    )

    # Clinicians table
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS clinicians (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL UNIQUE,
            full_name TEXT NOT NULL,
            specialization TEXT,
            license_number TEXT NOT NULL UNIQUE,
            created_at TEXT NOT NULL,
            updated_at TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
        """
    )

    # Patients table
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            clinician_id INTEGER NOT NULL,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            date_of_birth TEXT NOT NULL,
            gender TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT,
            FOREIGN KEY (clinician_id) REFERENCES clinicians(id)
        );
        """
    )

    # Activation tokens table
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS activation_tokens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            token_hash TEXT NOT NULL,
            expires_at TEXT NOT NULL,
            used_at TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
        """
    )

    conn.commit()
    conn.close()
