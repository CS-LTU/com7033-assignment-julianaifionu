from bson import ObjectId
from datetime import datetime, date


def to_object_id(id_value):
    # Ensures patient id is of ObjectId type
    if isinstance(id_value, ObjectId):
        return id_value
    return ObjectId(id_value)


def dob_to_age(dob_str, date_format="%Y-%m-%d"):
    """
    Converts a date of birth string to age in years.
    Returns 0 if dob is today, 0 if dob is in the future or invalid.
    """
    try:
        dob = datetime.strptime(dob_str, date_format).date()
    except ValueError:
        # Invalid date format
        return 0

    today = date.today()

    if dob > today:
        return 0

    age = today.year - dob.year

    if (today.month, today.day) < (dob.month, dob.day):
        age -= 1

    return age
