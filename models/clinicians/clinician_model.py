from models.db_sqlite import get_db
from models.auth.auth import hash_password
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
    return rows


def get_clinician_user_id(clinician_id):
    conn = get_db()
    cur = conn.cursor()
    
    cur.execute("SELECT user_id FROM clinicians WHERE id = ?", (clinician_id,))
    
    owner = cur.fetchone()
    conn.close()
    return owner
