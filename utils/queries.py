from utils.db_sqlite import get_db
from utils.auth import hash_password
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


def get_all_patients():
    """
    Returns every patient with their assigned clinician.
    """

    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT 
            patients.id AS patient_id,
            patients.first_name,
            patients.last_name,
            patients.date_of_birth,
            patients.gender,
            patients.address,
            patients.created_at AS patient_created_at,

            clinicians.id AS clinician_id,
            clinicians.full_name AS clinician_name,
            clinicians.specialization AS clinician_specialization

        FROM patients
        LEFT JOIN clinicians ON patients.clinician_id = clinicians.id

        ORDER BY patients.created_at DESC
        """
    )

    rows = cur.fetchall()
    conn.close()
    return rows


def get_all_patients_for_clinician(user_id):
    """
    Returns all patients assigned to a clinician using user_id.
    """

    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT id FROM clinicians WHERE user_id = ?", (user_id,))
    row = cur.fetchone()

    if not row:
        conn.close()
        return []

    clinician_id = row["id"]

    cur.execute(
        """
        SELECT
            patients.id AS patient_id,
            patients.first_name,
            patients.last_name,
            patients.date_of_birth,
            patients.gender,
            patients.created_at

        FROM patients
        WHERE patients.clinician_id = ?
        ORDER BY patients.created_at DESC
        """,
        (clinician_id,),
    )

    rows = cur.fetchall()
    conn.close()
    return rows
