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

    conn.close()
    return {"total": total, "active": active, "inactive": inactive}


def get_clinician_admin_stats():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM clinicians")
    total = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM clinicians WHERE is_archived = 1")
    archived = cur.fetchone()[0]

    # Active means: user account activated AND clinician not archived
    cur.execute(
        """
        SELECT COUNT(*) 
        FROM clinicians c 
        JOIN users u ON c.user_id = u.id
        WHERE u.is_active = 1 AND c.is_archived = 0
    """
    )
    active = cur.fetchone()[0]

    conn.close()
    return {
        "total": total,
        "active": active,
        "archived": archived,
    }


def get_patient_admin_stats():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM patients")
    total = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM patients WHERE is_archived = 1")
    archived = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM patients WHERE is_archived = 0")
    active = cur.fetchone()[0]

    # New patients today
    cur.execute(
        """
				SELECT COUNT(*)
				FROM patients
				WHERE DATE(created_at) = DATE('now', 'localtime')
				"""
    )
    new = cur.fetchone()[0]

    conn.close()

    return {
        "total": total,
        "active": active,
        "archived": archived,
        "new": new,
    }
