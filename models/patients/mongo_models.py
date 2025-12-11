from pymongo import MongoClient
from config import Config
from bson import ObjectId
from datetime import datetime, timezone
from services.decrypt_doc import decrypt_patient_doc
from services.encryption_service import encrypt_value
from models.patients.helpers import dob_to_age, to_object_id

_client = MongoClient(Config.MONGO_URI)
_mdb = _client[Config.MONGO_DB]
patients_collection = _mdb[Config.MONGO_PATIENTS_COL]


def create_patient(clinician_id, data, collection=None):
    """
    Create a new patient record with encrypted medical fields and insert into MongoDB.
    """
    collection = collection or patients_collection

    # Normalize names and compute age from dob
    age = dob_to_age(data["date_of_birth"])
    normalize_first_name = data.get("first_name").title()
    normalize_last_name = data.get("last_name").title()

    patient = {
        "_id": ObjectId(),
        "first_name": normalize_first_name,
        "last_name": normalize_last_name,
        "gender": data.get("gender"),
        "age": int(age),
        "ever_married": data.get("ever_married"),
        "work_type": data.get("work_type"),
        "smoking_status": data.get("smoking_status"),
        "residence_type": data.get("residence_type"),
        "created_by": clinician_id,  # SQLite user id
        "created_at": datetime.now(timezone.utc),
        "updated_at": None,
    }

    # Encrypt and add medical fields
    for field in Config.MEDICAL_FIELDS:
        value = data.get(field)
        if value is not None:
            patient[field] = encrypt_value(str(value))
        else:
            patient[field] = None

    collection.insert_one(patient)
    return str(patient["_id"])


def get_patient_admin_stats():
    # Return the total number of patients in the collection
    total = patients_collection.count_documents({})
    return {"total": total if total else 0}


def get_patient_clinician_stats():
    """
    Compute and aggregates patient data to provide an overview of key metrics
    relevant for clinician dashboard. It decrypts medical fields as necessary and computes
    statistics such as counts, distributions, and averages.
    """
    stats = {}

    # Fetch all patients
    all_docs = patients_collection.find()
    patients = [decrypt_patient_doc(d) for d in all_docs]

    stats["total"] = len(patients)

    # Stroke counts
    stroke_counts = {}
    for p in patients:
        stroke = p.get("stroke")
        stroke_counts[str(stroke)] = stroke_counts.get(str(stroke), 0) + 1
    stats["stroke_counts"] = stroke_counts

    # New patients today
    today_start = datetime.combine(datetime.today(), datetime.min.time())
    stats["new_today"] = sum(
        1 for p in patients if p.get("created_at") and p["created_at"] >= today_start
    )

    # Gender distribution among stroke patients
    gender_counts = {}
    for p in patients:
        if p.get("stroke") == 1:
            gender = p.get("gender", "Unknown")
            gender_counts[gender] = gender_counts.get(gender, 0) + 1
    stats["gender_counts"] = gender_counts

    # Average age & BMI among stroke patients
    ages = [
        p["age"]
        for p in patients
        if p.get("stroke") == 1 and isinstance(p.get("age"), (int, float))
    ]
    bmis = [
        p["bmi"]
        for p in patients
        if p.get("stroke") == 1 and isinstance(p.get("bmi"), (int, float))
    ]

    stats["avg_age"] = round(sum(ages) / len(ages), 1) if ages else 0
    stats["avg_bmi"] = round(sum(bmis) / len(bmis), 1) if bmis else 0

    # Work type distribution among stroke patients
    work_counts = {}
    for p in patients:
        if p.get("stroke") == 1:
            work = p.get("work_type", "Unknown")
            work_counts[work] = work_counts.get(work, 0) + 1
    stats["work_type_counts"] = work_counts

    return stats


def get_all_patients(created_by=None):
    """
    Fetch and decrypt all patient records.
    """
    query = {}
    if created_by is not None:
        query["created_by"] = created_by

    cursor = patients_collection.find(query).sort("created_at", -1)

    results = []
    for doc in cursor:
        patient = decrypt_patient_doc(doc)
        patient["id"] = str(doc["_id"])
        del patient["_id"]
        results.append(patient)

    return results


def get_first_10_patients(created_by=None):
    """
    Fetch first 10 patient records for use in the clinician dashboard.
    Args:
        created_by (int, optional): SQLite user_id of the clinician who created the patients.
        If None, fetches all 10 patients.
    Returns:
        List of patient documents.
    """
    query = {}
    if created_by is not None:
        query["created_by"] = created_by

    # Fetch only first 10 records, newest first
    patients_cursor = patients_collection.find(query).sort("created_at", -1).limit(10)

    # convert Mongo ObjectId to string
    formatted = []
    for p in patients_cursor:
        p["id"] = str(p["_id"])
        del p["_id"]
        formatted.append(p)

    return formatted


def delete_patient(patient_id):
    """
    Deletes a patient record from MongoDB.
    Args:
        patient_id: The MongoDB ObjectId of the patient to delete.
    Returns:
        bool: True if deleted, False if not found or unauthorized.
    """
    query = {"_id": to_object_id(patient_id)}
    result = patients_collection.delete_one(query)

    return result.deleted_count > 0


def get_patient_by_id(patient_id):
    """
    Fetch and decrypt a patient record.
    Args:
        patient_id: string or ObjectId
    Returns:
        dict or None
    """
    doc = patients_collection.find_one({"_id": to_object_id(patient_id)})

    if not doc:
        return None

    # decrypt and format id safely
    patient = decrypt_patient_doc(doc)
    patient["id"] = str(patient["_id"])

    return patient


def update_patient(patient_id, data, clinician_id):
    """
    Update a patient record in MongoDB with encrypted medical fields.
    """
    # Base document with non-medical fields
    document = {
        "first_name": data.get("first_name"),
        "last_name": data.get("last_name"),
        "gender": data.get("gender"),
        "age": int(data.get("age", 0)),
        "ever_married": data.get("ever_married"),
        "work_type": data.get("work_type"),
        "smoking_status": data.get("smoking_status"),
        "residence_type": data.get("residence_type"),
        "updated_by": clinician_id,
        "updated_at": datetime.now(timezone.utc),
    }

    # Encrypt only the medical fields
    for field in Config.MEDICAL_FIELDS:
        value = data.get(field)
        if value is not None:
            document[field] = encrypt_value(str(value))
        else:
            document[field] = None

    result = patients_collection.update_one(
        {"_id": to_object_id(patient_id)}, {"$set": document}
    )

    return result.modified_count == 1


def search_patient(search_query=None):
    if search_query:
        cursor = patients_collection.find(
            {
                "$or": [
                    {"first_name": {"$regex": search_query, "$options": "i"}},
                    {"last_name": {"$regex": search_query, "$options": "i"}},
                ]
            }
        )

        results = []
        for doc in cursor:
            patient = decrypt_patient_doc(doc)
            patient["id"] = str(doc["_id"])
            del patient["_id"]
            results.append(patient)

        return results

    # If no search term provided return all patients
    return get_all_patients()
