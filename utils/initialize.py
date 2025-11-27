import sqlite3
from utils.db_sqlite import init_sqlite_db, get_db
from utils.auth import hash_password
from utils.config import Config
from utils.services_logging import log_action
from utils.time_formatter import utc_now


def initialize():
    """
    Creates database tables, seeds the roles,
    and creates the default admin user if none exists.
    """

    try:
        init_sqlite_db()

        conn = get_db()
        cur = conn.cursor()

        # Seed roles for admin and clinician
        cur.execute("SELECT COUNT(1) FROM roles")
        roles_exist = cur.fetchone()[0] > 0

        if not roles_exist:
            cur.execute(
                "INSERT INTO roles (name, description) VALUES (?, ?)",
                ("admin", "System Administrator with full privileges"),
            )
            cur.execute(
                "INSERT INTO roles (name, description) VALUES (?, ?)",
                ("clinician", "Healthcare professional who manages patients"),
            )
            print("Seeded roles: admin, clinician")

        # Check if an admin user already exists
        cur.execute(
            "SELECT COUNT(1) FROM users JOIN roles ON users.role_id = roles.id WHERE roles.name = ?",
            ("admin",),
        )

        has_admin = cur.fetchone()[0] > 0

        # Create default admin user if none exists
        if not has_admin:
            admin_username = Config.ADMIN_USERNAME
            admin_password = Config.ADMIN_PASSWORD

            if not admin_username or not admin_password:
                raise ValueError(
                    "ADMIN_USERNAME and ADMIN_PASSWORD must be set in the environment."
                )

            if not Config.PASSWORD_PATTERN.fullmatch(admin_password):
                raise ValueError(
                    "Password must be 8–64 characters long and include at least one uppercase letter, "
                    "one lowercase letter, one digit, and one special character."
                )

            password_hash = hash_password(admin_password)

            # Get admin role ID
            cur.execute("SELECT id FROM roles WHERE name = 'admin'")
            role_id = cur.fetchone()["id"]

            # Insert admin user
            cur.execute(
                """
                INSERT INTO users (username, password_hash, role_id, is_active, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    admin_username.strip(),
                    password_hash,
                    role_id,
                    1,  # admin is auto-activated
                    utc_now(),
                ),
            )

            admin_id = cur.lastrowid
            conn.commit()
            conn.close()

            # Log the action
            try:
                log_action(
                    action="REGISTER_ADMIN",
                    user_id=admin_id,
                    details={"username": admin_username},
                )
            except Exception:
                print("Warning: Logging failed but admin user was still created.")

            print(f"Created default admin user: {admin_username}")

    except ValueError as e:
        print(f"[INIT ERROR] {e}")

    except sqlite3.Error as e:
        print(f"[SQLITE ERROR] {e}")

    except Exception as e:
        print(f"Unexpected error during initialization: {e}")
