from models.db_sqlite import get_db
from utils.time_formatter import utc_now
from models.auth.auth import get_user_by_id


def create_user(username, full_name, role_name, db=None):
    # Create a new user with the given username, full name, and role; sets account as inactive initially
    conn = db or get_db()
    cur = conn.cursor()

    cur.execute("SELECT id FROM roles WHERE name = ?", (role_name,))
    row = cur.fetchone()

    if not row:
        raise ValueError(f"Role '{role_name}' does not exist.")

    role_id = row["id"]
    time = utc_now()
    normalized_full_name = full_name.title()

    cur.execute(
        """
        INSERT INTO users (username, full_name, password_hash, role_id, is_active, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (username, normalized_full_name, None, role_id, 0, time),
    )

    new_user_id = cur.lastrowid

    conn.commit()

    if db is None:
        conn.close()

    return new_user_id


def get_all_user_roles():
    # Retrieve a list of all role names from the roles table
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT name FROM roles")
    rows = cur.fetchall()
    conn.close()
    return [row["name"] for row in rows] if rows else []


def update_user(user_id, data):
    # Update a user's full name and username based on the provided user ID
    username = data.get("username")
    full_name = data.get("full_name")
    
    if not username or not full_name:
        raise ValueError("Username and full name are required.")

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


def delete_user_service(user_id):
    """
    Deletes a user from the database; prevents deleting admin accounts
    """
    user = get_user_by_id(user_id)

    # User must exist
    if not user:
        raise ValueError("User does not exist.")

    # Prevent deleting admin accounts
    if user["role_name"].lower() == "admin":
        raise ValueError("Cannot delete admin account.")

    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        """
        DELETE FROM users
        WHERE id = ?
        """,
        (user_id,),
    )

    conn.commit()
    deleted = cur.rowcount == 1
    conn.close()

    return deleted
