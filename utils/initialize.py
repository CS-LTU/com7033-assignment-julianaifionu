import sqlite3
from utils.db_sqlite import init_sqlite_db, get_db
from utils.auth import hash_password
from utils.config import Config


def initialize():
    conn = None

    try:
        init_sqlite_db()

        conn = get_db()
        cur = conn.cursor()

        # Check if an admin already exists
        cur.execute("SELECT COUNT(1) FROM users WHERE role = ?", ("admin",))
        has_admin = cur.fetchone()[0] > 0

        if not has_admin:
            email = Config.ADMIN_EMAIL
            password = Config.ADMIN_PASSWORD

            if not email or not password:
                raise ValueError(
                    "ADMIN_EMAIL and ADMIN_PASSWORD must be set in the environment."
                )

            password_hash = hash_password(password)

            cur.execute(
                "INSERT INTO users (first_name, last_name, email, role, password_hash, is_active) VALUES (?, ?, ?, ?, ?, ?)",
                (
                    "System",
                    "Admin",
                    email.strip().lower(),
                    "admin",
                    password_hash,
                    True,
                ),
            )
            conn.commit()

    except ValueError as e:
        print(str(e))

    except sqlite3.Error:
        print(f"SQLite error during initialization: {e}")
        if conn:
            conn.rollback()

    except Exception as e:
        print(f"Unexpected error during initialization: {e}")
        if conn:
            conn.rollback()

    finally:
        if conn:
            try:
                conn.close()
            except:
                pass
