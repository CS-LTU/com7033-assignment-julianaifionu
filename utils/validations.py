from utils.config import Config
from utils.auth import get_user_by_email, authenticate_user


def validate_registration_form(first_name, last_name, email, role):
    if not (first_name and last_name and email and role):
        raise ValueError("All fields are required.")

    if not Config.EMAIL_PATTERN.fullmatch(email):
        raise ValueError("Email format is invalid.")

    if get_user_by_email(email):
        raise ValueError("A user with this email already exists.")


def validate_login_form(email, password):
    if not (email and password):
        raise ValueError("Please enter both email and password.")


def validate_activation_passwords(new_password, confirm_password):
    if not (new_password and confirm_password):
        raise ValueError("Please fill in all password fields.")

    if new_password != confirm_password:
        raise ValueError("Passwords do not match.")

    if len(new_password) < 8:
        raise ValueError("Password must be at least 8 characters long.")
