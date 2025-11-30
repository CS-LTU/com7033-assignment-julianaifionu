from models.db_sqlite import get_db
from utils.time_formatter import utc_now


def create_patient(clinician_id, first_name, last_name, date_of_birth, gender):
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


def get_patient_by_id(patient_id):
    conn = get_db()
    cur = conn.cursor()
    
    cur.execute("SELECT id, clinician_id FROM patients WHERE id = ?", (patient_id,))
    patient = cur.fetchone()
    
    conn.close()
    return patient
