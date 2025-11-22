import bcrypt
from utils.db_sqlite import get_db

"""Authentication utility functions."""


def hash_password(plain_password: str):
    """
    Hash user's plain text password using bcrypt.

    Args:
        plain_password (str): The plain text password entered by the user during registration.

    Returns:
        bytes: hashed password.
    """
    password_bytes = plain_password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password_bytes, salt)
    return hashed_password


def check_password(plain_password, hashed_password):
    """
    Compare a stored password hash with a user-provided password.

    Args:
        plain_password (str): The plain text password entered by the user during login.
        hashed_password (str): The hashed password retrieved from the database.

    Returns:
        bool: True if the passwords match, False otherwise.
    """

    # check_password_hash securely compares the hash and plain text password
    if hashed_password is None or plain_password is None:
        return False
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password)


def authenticate_user(
    email: str, plain_password: str, users: list[dict]
) -> dict | None:
    """
     Authenticate a user by email and password.

    Args:
         email (str): The user's email address (case-insensitive).
         plain_password (str): The user's plaintext password to verify.
         users (list[dict]): List of user dictionaries with 'email' and 'password' keys.

     Returns:
         dict | None: The user dict if credentials are correct, otherwise None.
    """

    # Normalize email to make lookup case-insensitive
    email = email.lower()

    for user in users:
        if user["email"].lower() == email and check_password(
            plain_password, user["password"]
        ):
            return user
    return None


def get_user_by_email(email: str) -> dict | None:
    """
    Find a user by their email address from the users table.

    Args:
        email (str): The email address to search for (case-insensitive).
    Returns:
        dict | None: The matching user dictionary if found, otherwise None.
    """
    
    conn = get_db()
    cur = conn.cursor()
    
    cur.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = cur.fetchone()
    
    conn.close()

    return user


def get_user_by_id(id: str, users: list[dict]) -> dict | None:
    """
    Find a user in the users list by user id.

    Args:
        id (str): The user id to search for.
        users (list[dict]): List of user dictionaries, each containing an 'id' key.

    Returns:
        dict | None: The matching user dictionary if found, otherwise None.
    """

    for user in users:
        if user["user_id"] == id:
            return user
    return None
