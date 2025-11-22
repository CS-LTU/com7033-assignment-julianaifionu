import os


class Config:
    SECRET_KEY = os.environ.get("STROKE_APP_SECRET_KEY", "my_dev_secret_key")
    BASE_DIR = os.getcwd()
    DB_PATH = os.path.join(BASE_DIR, "stroke_tracker.db")
