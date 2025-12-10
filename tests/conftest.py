import pytest
import sqlite3
import pytest


@pytest.fixture
def sqlite_test_db():
    """
    Provide a temporary in-memory SQLite database for testing.
    This DB is isolated, seeded with basic roles.
    """
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # Initialize tables
    cur.execute(
        """
        CREATE TABLE roles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT
        );
    """
    )
    
    cur.execute(
        """
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role_id INTEGER NOT NULL,
            username TEXT NOT NULL UNIQUE,
            full_name TEXT NOT NULL,
            password_hash TEXT,
            is_active BOOLEAN NOT NULL DEFAULT 0,
            is_archived BOOLEAN NOT NULL DEFAULT 0,
            archived_at TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT,
            FOREIGN KEY (role_id) REFERENCES roles(id)
        );
    """
    )
    
    cur.execute(
        """
        CREATE UNIQUE INDEX idx_users_username_unique ON users(username);
    """
    )
    
    cur.execute(
        """
        CREATE TABLE activation_tokens (
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

    # Seed default role
    cur.execute(
        "INSERT INTO roles (name, description) VALUES (?, ?)",
        ("admin", "clinician"),
    )
    conn.commit()

    # Yield connection to the test
    yield conn

    # Cleanup after test
    conn.close()
