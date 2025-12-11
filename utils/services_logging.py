from utils.time_formatter import utc_now
from pymongo import MongoClient
from config import Config

_client = MongoClient(Config.MONGO_URI)
_mdb = _client[Config.MONGO_DB]
logs_collection = _mdb[Config.MONGO_LOGS_COL]


def log_action(action, user_id, details=None):
    doc = {
        "action": action,
        "user_id": user_id,
        "details": details or {},
        "ts": utc_now(),
    }

    logs_collection.insert_one(doc)
