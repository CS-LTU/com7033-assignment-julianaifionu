from werkzeug.security import check_password_hash

"""Authentication utility functions."""


def check_password(password_hash, pwd):
    """
    Compare a stored password hash with a user-provided password.

    Args:
        password_hash (str): The hashed password retrieved from the database.
        pwd (str): The plain text password entered by the user during login.

    Returns:
        bool: True if the passwords match, False otherwise.
    """
    # check_password_hash securely compares the hash and plain text password
    if password_hash is None:
        return False
    return check_password_hash(password_hash, pwd)


def get_user_by_email(
    email: str, password: str, registered_users: list[dict]
) -> dict | None:
    """
    Return the user dict if the email and password match, else None.

    Args:
        email (str): The user's email address.
        password (str): The user's password (plaintext for now).
        registered_users (list): The list of registered user dictionaries.

    Returns:
        dict | None: The matched user dictionary, or None if not found.
    """

    # normalize email
    email = email.lower()

    for user in registered_users:
        if user["email"].lower() == email and check_password(
            user["password"], password
        ):
            return user
    return None
