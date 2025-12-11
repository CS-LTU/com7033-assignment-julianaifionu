from utils.time_formatter import utc_now
from pymongo import MongoClient
from config import Config

_client = MongoClient(Config.MONGO_URI)
_mdb = _client[Config.MONGO_DB]
logs_collection = _mdb[Config.MONGO_LOGS_COL]


def get_logs():
    # Fetch all log records for the auditor.
    log_cursor = logs_collection.find().sort("created_at", -1).limit(100)

    # convert Mongo ObjectId to string
    formatted = []
    for p in log_cursor:
        p["id"] = str(p["_id"])
        del p["_id"]
        formatted.append(p)

    return formatted
