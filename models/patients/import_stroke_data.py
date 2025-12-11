import os
import csv
from faker import Faker
from pymongo import MongoClient
from bson import ObjectId
from dotenv import load_dotenv
from datetime import datetime, timezone
from config import Config
from services.encryption_service import encrypt_value

load_dotenv() # Load env variables
fake = Faker() # Generate Random fake data e.g person's first name

_client = MongoClient(Config.MONGO_URI)
_mdb = _client[Config.MONGO_DB]
patients_collection = _mdb[Config.MONGO_PATIENTS_COL]

def seed_stroke_dataset(created_by=None):
    # Seeds initial stroke data from csv dataset
    dataset_dir = Config.DATASET_PATH
    filename = "healthcare_stroke_data.csv"
    file_path = os.path.join(dataset_dir, filename)

    if not os.path.isdir(dataset_dir):
        print(f"Dataset folder not found: {dataset_dir}")
        return
    if not os.path.isfile(file_path):
        print(f"CSV file not found: {file_path}")
        return
    if not filename.lower().endswith(".csv"):
        print(f"Not a CSV file: {filename}")
        return
    if patients_collection.count_documents({"source": "stroke_dataset"}) > 0:
        print("Stroke dataset already imported. Skipping...")
        return

    print(f"Importing stroke dataset from: {file_path}")

    with open(file_path, newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        records = []
        for row in reader:
            row.pop("id", None)
            first_name = fake.first_name()
            last_name = fake.last_name()
            row["first_name"] = first_name
            row["last_name"] = last_name
            row["source"] = "stroke_dataset"
            row["created_by"] = created_by
            row["created_at"] = datetime.now(timezone.utc)
            row["updated_at"] = None
            
            # Convert to proper types (int)
            for key in ["hypertension", "heart_disease", "stroke", "age"]:
                try:
                    row[key] = int(float(row[key]))
                except Exception:
                    row[key] = None
                    
            # Convert to proper types (float)
            for key in ["bmi", "avg_glucose_level"]:
                try:
                    row[key] = float(row[key])
                except Exception:
                    row[key] = None
            
            if "Residence_type" in row:
                row["residence_type"] = row.pop("Residence_type")
            
            numeric_fields = ["hypertension", "heart_disease", "stroke", "age", "bmi", "avg_glucose_level"]
            # Turn all strings to lowercase for normalization
            for key, value in list(row.items()):
                if isinstance(value, str) and key not in ["first_name", "last_name"] and key not in numeric_fields:
                    row[key] = value.lower()

            # Encrypt only the medical fields
            for field in Config.MEDICAL_FIELDS:
                if field in row and row[field] is not None:
                    # store encrypted dict
                    row[field] = encrypt_value(str(row[field]))
                else:
                    row[field] = None

            row["_id"] = ObjectId()
            records.append(row)

        if records:
            patients_collection.insert_many(records, ordered=False)
        print("Stroke dataset imported successfully!")
