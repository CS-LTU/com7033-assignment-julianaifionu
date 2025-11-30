from utils.time_formatter import utc_now
from pymongo import MongoClient
from utils.config import Config

_client = MongoClient(Config.MONGO_URI)
_mdb = _client[Config.MONGO_DB]
medical_history_collection = _mdb[Config.MONGO_MEDICAL_HISTORY_COL]
lifestyle_collection = _mdb[Config.MONGO_LIFESTYLE_COL]


def insert_medical_history(patient_id, data):
    document = {
        "patient_id": patient_id,
        "hypertension": int(data.get("hypertension")),
        "heart_disease": int(data.get("heart_disease")),
        "avg_glucose_level": float(data.get("avg_glucose_level")),
        "bmi": float(data.get("bmi")),
        "stroke": int(data.get("stroke")),
        "created_at": utc_now(),
        "updated_at": "N/A",
    }

    medical_history_collection.insert_one(document)


def insert_lifestyle(patient_id, data):
    document = {
        "patient_id": patient_id,
        "ever_married": data.get("ever_married"),
        "work_type": data.get("work_type"),
        "resident_type": data.get("resident_type"),
        "smoking_status": data.get("smoking_status"),
        "created_at": utc_now(),
        "updated_at": "N/A",
    }

    lifestyle_collection.insert_one(document)


def get_medical_history(patient_id):
    return medical_history_collection.find_one({"patient_id": patient_id})


def get_lifestyle(patient_id):
    return lifestyle_collection.find_one({"patient_id": patient_id})


def update_medical_history(patient_id, data):
    medical_history_collection.update_one(
        {"patient_id": patient_id},
        {
            "$set": {
                "hypertension": int(data.get("hypertension")),
                "heart_disease": int(data.get("heart_disease")),
                "avg_glucose_level": float(data.get("avg_glucose_level")),
                "bmi": float(data.get("bmi")),
                "stroke": int(data.get("stroke")),
                "updated_at": utc_now(),
            }
        },
        upsert=True,
    )


def update_lifestyle(patient_id, data):
    lifestyle_collection.update_one(
        {"patient_id": patient_id},
        {
            "$set": {
                "ever_married": data.get("ever_married"),
                "work_type": data.get("work_type"),
                "resident_type": data.get("resident_type"),
                "smoking_status": data.get("smoking_status"),
                "updated_at": utc_now(),
            }
        },
        upsert=True,
    )



