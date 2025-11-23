import os, re
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.environ.get("STROKE_APP_SECRET_KEY")
    ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL")
    ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")
    BASE_DIR = os.getcwd()
    DB_PATH = os.path.join(BASE_DIR, "stroke_tracker.db")
    EMAIL_PATTERN = re.compile(r"^[\w\.-]+@[\w\.-]+\.[A-Za-z]{2,}$")

    # Mongo
    MONGO_URI = os.environ.get("MONGO_URI")
    MONGO_DB = "stroke_tracker_db"
    MONGO_LOGS_COL = "logs"
