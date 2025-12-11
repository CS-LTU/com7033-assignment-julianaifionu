from config import Config
from models.auth.auth import get_user_by_username
from config import Config
from models.users.user_model import get_all_user_roles


def validate_registration_form(username, full_name, role_name):
    if not (username and full_name and role_name):
        raise ValueError("All fields are required.")

    # Username format validation
    if not Config.USERNAME_PATTERN.fullmatch(username):
        raise ValueError(
            "Username is invalid. Use 3-20 characters: letters, numbers, underscores."
        )
    
    # Full name format validation
    if not Config.FULLNAME_PATTERN.fullmatch(full_name):
        raise ValueError(
            "Full name is invalid. Must contain atleast 2 separate names"
        )

    # Check that role exists
    if role_name not in get_all_user_roles():
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
            "Password must be 8-64 characters long and include at least one uppercase letter, "
            "one lowercase letter, one digit, and one special character."
        )
