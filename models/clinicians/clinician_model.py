from models.db_sqlite import get_db
from utils.time_formatter import utc_now


def create_clinician_profile(user_id, full_name, specialization, license_number):
    conn = get_db()
    cur = conn.cursor()

    time = utc_now()

    cur.execute(
        """
        INSERT INTO clinicians (user_id, full_name, specialization, license_number, created_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (user_id, full_name, specialization, license_number, time),
    )

    conn.commit()
    conn.close()


def get_all_clinicians():
    """
    Returns all clinicians data.
    """

    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT 
            users.id AS user_id,
            users.username,
            users.is_active,
            users.created_at AS user_created_at,
            roles.name AS role_name,

            clinicians.id AS clinician_id,
            clinicians.full_name,
            clinicians.specialization,
            clinicians.license_number,
            clinicians.is_archived,
						clinicians.archived_at,
            clinicians.created_at AS clinician_created_at

        FROM users
        JOIN roles ON users.role_id = roles.id
        JOIN clinicians ON clinicians.user_id = users.id
        WHERE roles.name = 'clinician'
        ORDER BY clinicians.created_at DESC
        """
    )

    rows = cur.fetchall()
    conn.close()
    return list(rows) if rows else []


def get_clinician_user_id(clinician_id):
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT user_id FROM clinicians WHERE id = ?", (clinician_id,))

    row = cur.fetchone()
    conn.close()
    return row["user_id"] if row else None


def get_user_clinician_id(user_id):
    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        "SELECT id FROM clinicians WHERE user_id = ?",
        (user_id,),
    )

    row = cur.fetchone()
    conn.close()
    return row["id"] if row else None

def get_clinician_by_id(clinician_id):
    """
    Fetches a clinician and their associated user account details.
    """
    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT 
            clinicians.id AS clinician_id,
            clinicians.user_id,
            clinicians.full_name,
            clinicians.specialization,
            clinicians.license_number,
            clinicians.is_archived,
						clinicians.archived_at,
            clinicians.created_at AS clinician_created_at,
            
            users.id AS user_id,
            users.username,
            users.is_active,
            users.created_at AS user_created_at,
            roles.name AS role_name

        FROM clinicians
        JOIN users ON users.id = clinicians.user_id
        JOIN roles ON users.role_id = roles.id
        WHERE clinicians.id = ?
        """,
        (clinician_id,),
    )

    row = cur.fetchone()
    conn.close()

    return row if row else None


def archive_clinician_service(clinician_id):
    clinician = get_clinician_by_id(clinician_id)

    if not clinician:
        raise ValueError("Clinician not found.")

    if clinician["is_archived"]:
        raise ValueError("Clinician is already archived.")

    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        """
			UPDATE clinicians
			SET is_archived = 1, archived_at = ?
			WHERE id = ?
			""",
        (utc_now(), clinician_id),
    )

    conn.commit()
    conn.close()


def is_clinician_archived(clinician_id):
    clinician = get_clinician_by_id(clinician_id)
    if not clinician:
        raise ValueError("Clinician not found.")
    return clinician["is_archived"]


def update_clinician(clinician_id, data):
    full_name = data.get("full_name")
    specialization = data.get("specialization")
    license_number = data.get("license_number")

    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        """
						UPDATE clinicians 
						SET full_name = ?, specialization = ?, license_number = ?
						WHERE id = ?
						""",
        (full_name, specialization, license_number, clinician_id),
    )

    conn.commit()
    conn.close()


def get_clinician_dashboard_stats(clinician_id):
    conn = get_db()
    cur = conn.cursor()

    # Total patients
    cur.execute(
        """
        SELECT COUNT(*)
        FROM patients 
        WHERE clinician_id = ?
    """,
        (clinician_id,),
    )
    total = cur.fetchone()[0]

    # Active patients
    cur.execute(
        """
        SELECT COUNT(*)
        FROM patients 
        WHERE is_archived = 0 AND clinician_id = ?
    """,
        (clinician_id,),
    )
    active = cur.fetchone()[0]

    # Archived patients
    cur.execute(
        """
        SELECT COUNT(*)
        FROM patients 
        WHERE is_archived = 1 AND clinician_id = ?
    """,
        (clinician_id,),
    )
    archived = cur.fetchone()[0]

    # New patients today
    cur.execute(
        """
        SELECT COUNT(*)
        FROM patients
        WHERE DATE(created_at) = DATE('now', 'localtime')
        AND clinician_id = ?
    """,
        (clinician_id,),
    )
    new = cur.fetchone()[0]

    conn.close()

    return {
        "total": total,
        "active": active,
        "archived": archived,
        "new": new,
    }
