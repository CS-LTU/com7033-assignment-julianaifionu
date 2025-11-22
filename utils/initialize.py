import os
from utils.db_sqlite import init_sqlite_db, get_db
from utils.auth import hash_password
from utils.config import Config


def initialize():
    init_sqlite_db()
    conn = get_db()
    cur = conn.cursor()

    try:
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
    except (ValueError, Exception) as e:
        print("Admin initialization error")
        conn.rollback()
    finally:
        conn.close()
