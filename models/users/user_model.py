from models.db_sqlite import get_db
from models.auth.auth import hash_password
from utils.time_formatter import utc_now


def create_user(username, role_name):
    conn = get_db()
    cur = conn.cursor()

    # Get user role ID
    cur.execute("SELECT id FROM roles WHERE name = ?", (role_name,))
    row = cur.fetchone()

    if not row:
        raise ValueError(f"Role '{role_name}' does not exist.")

    role_id = row["id"]
    time = utc_now()

    cur.execute(
        """
        INSERT INTO users (username, password_hash, role_id, is_active, created_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (username.strip(), None, role_id, 0, time),
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
