import os
import csv
from pymongo import MongoClient
from config import Config
from faker import Faker
from utils.time_formatter import utc_now

fake = Faker()
_client = MongoClient(Config.MONGO_URI)
_mdb = _client[Config.MONGO_DB]
patients_collection = _mdb[Config.MONGO_PATIENTS_COL]


def seed_stroke_dataset(created_by=None):
    """
    Import Stroke CSV dataset into MongoDB. Skips if already seeded.
    """

    # Path to dataset folder
    dataset_dir = Config.DATASET_PATH

    # CSV filename
    filename = "healthcare_stroke_data.csv"
    file_path = os.path.join(dataset_dir, filename)

    # Validate folder exists
    if not os.path.isdir(dataset_dir):
        print(f"Dataset folder not found: {dataset_dir}")
        return

    # Validate file exists
    if not os.path.isfile(file_path):
        print(f"CSV file not found: {file_path}")
        return

    # Validate extension to ensure only csv is imported
    if not filename.lower().endswith(".csv"):
        print(f"Not a CSV file: {filename}")
        return

    # Skip if already imported
    if patients_collection.count_documents({"source": "stroke_dataset"}) > 0:
        print("Stroke dataset already imported. Skipping...")
        return

    print(f"Importing stroke dataset from: {file_path}")

    with open(file_path, newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        records = []
        numeric_fields = [
            "hypertension",
            "heart_disease",
            "stroke",
            "age",
            "bmi",
            "avg_glucose_level",
        ]
        for row in reader:
            # Generate random first and last name for all the rows
            first_name = fake.first_name()
            last_name = fake.last_name()

            row.pop("id", None)
            row["first_name"] = first_name
            row["last_name"] = last_name
            row["source"] = "stroke_dataset"
            row["created_by"] = created_by
            row["created_at"] = utc_now()

            # Convert to integer
            for key in ["hypertension", "heart_disease", "stroke", "age"]:
                row[key] = int(float(row[key]))

            # Convert numeric floats
            for key in ["bmi", "avg_glucose_level"]:
                try:
                    row[key] = float(row[key])
                except ValueError:
                    continue

            # Normalize residence_type
            if "Residence_type" in row:
                row["residence_type"] = row.pop("Residence_type")  # rename key

            # Normalize string values to lowercase
            for key, value in row.items():
                if (
                    isinstance(value, str)
                    and key not in ["first_name", "last_name"]
                    and key not in numeric_fields
                ):
                    row[key] = value.lower()

            records.append(row)
        if records:
            patients_collection.insert_many(records, ordered=False)

        print("Stroke dataset imported successfully!")
