from models.db_sqlite import get_db
from utils.time_formatter import utc_now


def create_patient(clinician_id, data):
    first_name = data.get("first_name", "").strip()
    last_name = data.get("last_name", "").strip()
    date_of_birth = data.get("date_of_birth", "").strip()
    gender = data.get("gender", "").strip()

    if not all([first_name, last_name, date_of_birth, gender]):
        raise ValueError("All demographic fields are required.")

    conn = get_db()
    conn = get_db()
    cur = conn.cursor()
    timestamp = utc_now()

    cur.execute(
        """
        INSERT INTO patients (clinician_id, first_name, last_name, date_of_birth, gender, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """,
        (clinician_id, first_name, last_name, date_of_birth, gender, timestamp),
    )

    patient_id = cur.lastrowid
    conn.commit()
    conn.close()

    return patient_id


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
            patients.created_at AS patient_created_at,
            patients.is_archived,

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
    return list(rows) if rows else []


def get_patient_by_id(patient_id):
    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT id, clinician_id, first_name, last_name, date_of_birth, gender, created_at, is_archived, archived_at
        FROM patients 
        WHERE id = ?
    		""",
        (patient_id,),
    )

    row = cur.fetchone()

    conn.close()
    return row


def update_patient(patient_id, data):
    first_name = data.get("first_name")
    last_name = data.get("last_name")
    date_of_birth = data.get("date_of_birth")
    gender = data.get("gender")

    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        """
						UPDATE patients 
						SET first_name = ?, last_name = ?, date_of_birth = ?, gender = ?
						WHERE id = ?
						""",
        (first_name, last_name, date_of_birth, gender, patient_id),
    )

    conn.commit()
    conn.close()


def archive_patient_service(patient_id):
    patient = get_patient_by_id(patient_id)

    if not patient:
        raise ValueError("Patient not found.")

    if patient["is_archived"]:
        raise ValueError("Patient is already archived.")

    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        """
				UPDATE patients
				SET is_archived = 1,
						archived_at = ?
				WHERE id = ?;
				""",
        (utc_now(), patient_id),
    )
    conn.commit()
    conn.close()


def is_patient_archived(patient_id):
    patient = get_patient_by_id(patient_id)
    if not patient:
        raise ValueError("Patient not found.")
    return patient["is_archived"]


def total_archived_patients_count():
    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        "SELECT COUNT(*) AS total_archived_patients FROM patients WHERE is_archived = 1"
    )
    row = cur.fetchone()
    conn.close()

    return row["total_archived_patients"] if row else 0


def total_active_patients_count():
    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        "SELECT COUNT(*) AS total_active_patients FROM patients WHERE is_archived = 0"
    )
    row = cur.fetchone()
    conn.close()

    return row["total_active_patients"] if row else 0


def new_patients_today_count():
    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        """
				SELECT COUNT(*) AS new_patients_today
				FROM patients
				WHERE DATE(created_at) = DATE('now', 'localtime')
				"""
    )

    row = cur.fetchone()
    conn.close()

    return row["new_patients_today"] if row else 0
