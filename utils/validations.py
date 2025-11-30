from utils.config import Config
from models.auth.auth import get_user_by_username
from utils.config import Config


def validate_registration_form(username, license_number, role_name):
    if not (username and role_name):
        raise ValueError("All fields are required.")

    # Username format validation
    if not Config.USERNAME_PATTERN.fullmatch(username):
        raise ValueError(
            "Username is invalid. Use 3–20 characters: letters, numbers, underscores."
        )

    # Licence number format validation
    if not Config.LICENSE_NUMBER_PATTERN.fullmatch(license_number):
        raise ValueError(
            "License number is invalid. Format: 3 uppercase letters followed by 4–6 digits"
        )

    # Check that role exists
    if role_name not in ("admin", "clinician"):
        raise ValueError("Invalid role selected.")

    if get_user_by_username(username):
        raise ValueError("A user with this username already exists.")


def validate_login_form(username, password):
    if not (username and password):
        raise ValueError("Please enter both username and password.")


def validate_activation_passwords(new_password, confirm_password):
    if not (new_password and confirm_password):
        raise ValueError("Please fill in all password fields.")

    if new_password != confirm_password:
        raise ValueError("Passwords do not match.")

    if not Config.PASSWORD_PATTERN.fullmatch(new_password):
        raise ValueError(
            "Password must be 8–64 characters long and include at least one uppercase letter, "
            "one lowercase letter, one digit, and one special character."
        )
