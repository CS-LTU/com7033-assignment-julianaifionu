from utils.time_formatter import utc_now
from pymongo import MongoClient
from config import Config
from bson import ObjectId
from datetime import datetime, date

_client = MongoClient(Config.MONGO_URI)
_mdb = _client[Config.MONGO_DB]
patients_collection = _mdb[Config.MONGO_PATIENTS_COL]


# helper function
def to_object_id(id_value):
    # Ensures patient id is of ObjectId type
    if isinstance(id_value, ObjectId):
        return id_value
    return ObjectId(id_value)


def dob_to_age(dob_str, date_format="%Y-%m-%d"):
    """
    Converts a date of birth string to age in years.
    Args:
        dob_str (str): Date of birth from form, e.g., "1990-08-25"
        date_format (str): Format of the input string (default: "%Y-%m-%d")
    Returns:
        int: Age in years
    """
    try:
        dob = datetime.strptime(dob_str, date_format).date()
    except ValueError:
        # Invalid date format
        return None

    today = date.today()
    age = today.year - dob.year

    # Subtract 1 if birthday hasn't occurred yet this year
    if (today.month, today.day) < (dob.month, dob.day):
        age -= 1

    return age


def create_patient(clinician_id, data, collection=None):
    # Create a new patient record with provided data and insert it into the patients collection
    collection = collection or patients_collection

    age = dob_to_age(data["date_of_birth"])
    patient = {
        "_id": ObjectId(),
        "first_name": data.get("first_name"),
        "last_name": data.get("last_name"),
        "gender": data.get("gender"),
        "age": int(age),
        "hypertension": int(data.get("hypertension")),
        "heart_disease": int(data.get("heart_disease")),
        "ever_married": data.get("ever_married"),
        "work_type": data.get("work_type"),
        "residence_type": data.get("residence_type"),
        "avg_glucose_level": float(data.get("avg_glucose_level", 0)),
        "bmi": float(data.get("bmi", 0)) if data.get("bmi") not in ["", None] else None,
        "smoking_status": data.get("smoking_status"),
        "stroke": int(data.get("stroke")),
        "created_by": clinician_id,  # the user id from SQLite
        "created_at": utc_now(),
        "updated_at": None,
    }
    collection.insert_one(patient)
    return str(patient["_id"])


def get_patient_admin_stats():
    # Return the total number of patients in the collection
    total = patients_collection.count_documents({})
    return {"total": total if total else 0}


def get_patient_clinician_stats():
    """
    Returns general stats for clinician dashboard:
    - total patients
    - stroke vs non-stroke
    - gender distribution
    - New patients today
    - average age & BMI
    - work type distribution
    """
    stats = {}

    # Total patients
    stats["total"] = patients_collection.count_documents({})

    # Stroke counts
    stroke_pipeline = [{"$group": {"_id": "$stroke", "count": {"$sum": 1}}}]
    stroke_counts = list(patients_collection.aggregate(stroke_pipeline))
    stats["stroke_counts"] = {str(doc["_id"]): doc["count"] for doc in stroke_counts}

    # New patients today
    today_start = datetime.combine(datetime.today(), datetime.min.time())
    stats["new_today"] = patients_collection.count_documents(
        {"created_at": {"$gte": today_start}}
    )

    # Gender distribution among stroke patients
    gender_pipeline = [
        {"$match": {"stroke": 1}},
        {"$group": {"_id": "$gender", "count": {"$sum": 1}}},
    ]
    gender_counts = list(patients_collection.aggregate(gender_pipeline))
    stats["gender_counts"] = {doc["_id"]: doc["count"] for doc in gender_counts}

    # Average age among stroke patients
    avg_age_pipeline = [
        {"$match": {"stroke": 1, "age": {"$exists": True, "$ne": None, "$ne": ""}}},
        {"$addFields": {"numericAge": {"$toDouble": "$age"}}},
        {"$group": {"_id": None, "avg_age": {"$avg": "$numericAge"}}},
    ]
    result = list(patients_collection.aggregate(avg_age_pipeline))
    stats["avg_age"] = round(result[0]["avg_age"], 1) if result else 0

    # Average BMI among stroke patients
    avg_bmi_pipeline = [
        {"$match": {"stroke": 1, "bmi": {"$exists": True, "$ne": None, "$ne": ""}}},
        {
            "$addFields": {
                "numericBMI": {
                    "$convert": {
                        "input": "$bmi",
                        "to": "double",
                        "onError": None,
                        "onNull": None,
                    }
                }
            }
        },
        {"$match": {"numericBMI": {"$ne": None}}},
        {"$group": {"_id": None, "avg_bmi": {"$avg": "$numericBMI"}}},
    ]
    avg_bmi = list(patients_collection.aggregate(avg_bmi_pipeline))
    stats["avg_bmi"] = round(avg_bmi[0]["avg_bmi"], 1) if avg_bmi else 0

    # Work type distribution among stroke patients
    work_pipeline = [
        {"$match": {"stroke": 1}},
        {"$group": {"_id": "$work_type", "count": {"$sum": 1}}},
    ]
    work_counts = list(patients_collection.aggregate(work_pipeline))
    stats["work_type_counts"] = {doc["_id"]: doc["count"] for doc in work_counts}

    return stats


def get_all_patients(created_by=None):
    """
    Fetch all patient records.
    Args:
        created_by (int, optional): SQLite user_id of the clinician who created the patients.
        If None, fetches all patients (admin view).
    Returns:
        List of patient documents.
    """
    query = {}
    if created_by is not None:
        query["created_by"] = created_by

    patients_cursor = patients_collection.find(query).sort("created_at", -1).limit(100)

    # convert Mongo ObjectId to string
    formatted = []
    for p in patients_cursor:
        p["id"] = str(p["_id"])
        del p["_id"]
        formatted.append(p)

    return formatted


def get_first_10_patients(created_by=None):
    """
    Fetch first 10 patient records for use in the dashboard.
    Args:
        created_by (int, optional): SQLite user_id of the clinician who created the patients.
        If None, fetches all 10 patients (admin view).
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
    Check if a patient record exists in MongoDB.
    Args:
        patient_id: MongoDB ObjectId of the patient.
    Returns:
        dict: patient's record if found else None
    """
    patient = patients_collection.find_one({"_id": to_object_id(patient_id)})
    patient["id"] = str(patient["_id"])
    return patient if patient else None


def update_patient(patient_id, data, clinician_id):
    # Update patient fields in MongoDB
    document = {
        "first_name": data.get("first_name"),
        "last_name": data.get("last_name"),
        "gender": data.get("gender"),
        "age": int(data.get("age", 0)),
        "hypertension": bool(data.get("hypertension")),
        "heart_disease": bool(data.get("heart_disease")),
        "ever_married": data.get("ever_married"),
        "work_type": data.get("work_type"),
        "residence_type": data.get("residence_type"),
        "avg_glucose_level": float(data.get("avg_glucose_level", 0)),
        "bmi": float(data.get("bmi", 0)) if data.get("bmi") not in ["", None] else None,
        "smoking_status": data.get("smoking_status"),
        "stroke": bool(data.get("stroke")),
        "updated_by": clinician_id,
        "updated_at": utc_now(),
    }

    result = patients_collection.update_one(
        {"_id": to_object_id(patient_id)}, {"$set": document}
    )

    return result.modified_count == 1


def search_patient(search_query=None):
    if search_query:
        # Search patients by first_name or last_name (case-insensitive)
        patients = patients_collection.find(
            {
                "$or": [
                    {"first_name": {"$regex": search_query, "$options": "i"}},
                    {"last_name": {"$regex": search_query, "$options": "i"}},
                ]
            }
        )
        formatted = []
        for p in patients:
            p["id"] = str(p["_id"])
            del p["_id"]
            formatted.append(p)
        return formatted
    else:
        patients = get_all_patients()
    return patients
