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


def find_user(email: str, password: str, users: list[dict]) -> dict | None:
    """
     Authenticate a user by email and password.

    Args:
         email (str): The user's email address (case-insensitive).
         password (str): The user's plaintext password to verify.
         users (list[dict]): List of user dictionaries with 'email' and 'password' keys.

     Returns:
         dict | None: The user dict if credentials are correct, otherwise None.
    """

    # Normalize email to make lookup case-insensitive
    email = email.lower()

    for user in users:
        if user["email"].lower() == email and check_password(
            user["password"], password
        ):
            return user
    return None


def get_user_by_email(email: str, users: list[dict]) -> dict | None:
    """
    Find a user in the users list by their email address.

    Args:
        email (str): The email address to search for (case-insensitive).
        users (list[dict]): List of user dictionaries, each containing an 'email' key.

    Returns:
        dict | None: The matching user dictionary if found, otherwise None.
    """

    # Normalize email to avoid case sensitivity issues
    email = email.lower().strip()

    for user in users:
        if user["email"].lower() == email:
            return user
    return None
