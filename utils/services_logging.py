from datetime import datetime, timezone
from pymongo import MongoClient
from utils.config import Config

_client = MongoClient(Config.MONGO_URI)
_mdb = _client[Config.MONGO_DB]
logs_collection = _mdb[Config.MONGO_LOGS_COL]


def log_action(action, actor_uid, details=None):
    doc = {
        "action": action,
        "actor_user_id": actor_uid,
        "details": details or {},
        "ts": datetime.now(timezone.utc),
    }

    try:
        logs_collection.insert_one(doc)
    except Exception as e:
        print("Log insert failed:", e)
