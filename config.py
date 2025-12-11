import os, re
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.environ.get("STROKE_APP_SECRET_KEY")
    ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME")
    ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")
    BASE_DIR = os.getcwd()
    DB_PATH = os.path.join(BASE_DIR, "healthcare_system.db")
    DATASET_PATH = os.path.join(BASE_DIR, "dataset")
    USERNAME_PATTERN = re.compile(r"^[a-zA-Z0-9_]{3,20}$")
    FULLNAME_PATTERN = re.compile(r"^[A-Za-z]+(?:[ '-][A-Za-z]+)+$")
    LICENSE_NUMBER_PATTERN = re.compile(r"^[A-Z]{2,3}\d{4,6}$")
    PASSWORD_PATTERN = re.compile(
        r"""
    ^(?=.*[a-z])           # at least one lowercase
    (?=.*[A-Z])            # at least one uppercase
    (?=.*\d)               # at least one digit
    (?=.*[@$!%*?&.,;:_\-]) # at least one special character
    [A-Za-z\d@$!%*?&.,;:_\-]{8,64}$  # allowed chars & length
    """,
        re.VERBOSE,
    )

    # Mongo
    MONGO_URI = os.environ.get("MONGO_URI")
    MONGO_DB = "healthcare_system_db"
    MONGO_LOGS_COL = "logs"
    MONGO_PATIENTS_COL = "patients"
    
    # Fields to encrypt/decrypt
    MEDICAL_FIELDS = [
        "hypertension",
        "heart_disease",
        "stroke",
        "bmi",
        "avg_glucose_level",
    ]
