from models.db_sqlite import get_db


def get_user_admin_stats():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM users")
    total = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM users WHERE is_active = 1")
    active = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM users WHERE is_active = 0")
    inactive = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM users WHERE is_archived= 1")
    archive = cur.fetchone()[0]

    conn.close()
    return {"total": total, "active": active, "inactive": inactive, "archived": archive}


def get_all_users():
    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        """
				SELECT 
						users.id AS user_id,
						users.username,
						users.full_name,
						users.is_active,
						users.is_archived,
						users.created_at AS user_created_at,
						roles.name AS role_name
				FROM users
				JOIN roles ON users.role_id = roles.id
				ORDER BY users.created_at DESC
				"""
    )

    rows = cur.fetchall()
    print('users', rows)
    users = rows if rows else []

    conn.close()
    return users
