from models.db_sqlite import get_db
from models.auth.auth import hash_password
from utils.time_formatter import utc_now
from models.auth.auth import get_user_by_id


def create_user(username, full_name, role_name):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id FROM roles WHERE name = ?", (role_name,))
    row = cur.fetchone()

    if not row:
        raise ValueError(f"Role '{role_name}' does not exist.")

    role_id = row["id"]
    time = utc_now()

    cur.execute(
        """
        INSERT INTO users (username, full_name, password_hash, role_id, is_active, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (username, full_name, None, role_id, 0, time),
    )

    new_user_id = cur.lastrowid

    conn.commit()
    conn.close()

    return new_user_id


def update_user_activation(user_id, new_password):
    conn = get_db()
    cur = conn.cursor()

    password_hash = hash_password(new_password)
    time = utc_now()

    cur.execute(
        """
        UPDATE users
        SET password_hash = ?, is_active = ?, updated_at = ?
        WHERE id = ?
        """,
        (password_hash, 1, time, user_id),
    )

    conn.commit()
    conn.close()


def get_all_user_roles():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT name FROM roles")
    rows = cur.fetchall()
    conn.close()
    return [row["name"] for row in rows] if rows else []


def is_user_archived(user_id):
    user = get_user_by_id(user_id)
    if not user:
        raise ValueError("User not found.")
    return user["is_archived"]


def update_user(user_id, data):
    username = data.get("username")
    full_name = data.get("full_name")

    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        """
						UPDATE users 
						SET full_name = ?, username = ?
						WHERE id = ?
						""",
        (full_name, username, user_id),
    )

    conn.commit()
    conn.close()


def archive_user_service(user_id):
    user = get_user_by_id(user_id)

    if user["role_name"] == "admin":
        raise ValueError("Can not archive admin account.")

    archived = is_user_archived(user_id)

    if archived:
        raise ValueError("User is already archived.")

    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        """
			UPDATE users
			SET is_archived = 1, archived_at = ?
			WHERE id = ?
			""",
        (utc_now(), user_id),
    )

    conn.commit()
    conn.close()
