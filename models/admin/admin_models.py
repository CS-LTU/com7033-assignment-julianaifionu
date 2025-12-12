from models.db_sqlite import get_db


def get_user_admin_stats():
    # Get users stats for admin dashboard view
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM users")
    total = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM users WHERE is_active = 1")
    active = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM users WHERE is_active = 0")
    inactive = cur.fetchone()[0]

    conn.close()
    return {"total": total, "active": active, "inactive": inactive}


def get_all_users():
    # Fetch all users from the database for admin management
    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        """
				SELECT 
						users.id AS user_id,
						users.username,
						users.full_name,
						users.is_active,
						users.created_at AS user_created_at,
						roles.name AS role_name
				FROM users
				JOIN roles ON users.role_id = roles.id
				ORDER BY users.created_at DESC
				"""
    )

    rows = cur.fetchall()
    users = rows if rows else []

    conn.close()
    return users


def search_user(search_query=None):
    # Search for user by full_name or username
    if search_query:
        conn = get_db()
        cur = conn.cursor()

        search_pattern = f"%{search_query}%"
        cur.execute(
            """
            SELECT 
								users.id AS user_id,
								users.username,
								users.full_name,
								users.is_active,
								users.created_at AS user_created_at,
								roles.name AS role_name
						FROM users
						JOIN roles ON users.role_id = roles.id
            WHERE full_name LIKE ?
            OR username LIKE ?
						ORDER BY users.created_at DESC
            """,
            (search_pattern, search_pattern),
        )
        rows = cur.fetchall()
        users = rows if rows else []
        conn.close()
    else:
        users = get_all_users()

    return users
