import bcrypt, sqlite3
from utils.db_sqlite import get_db

"""Authentication utility functions."""


def hash_password(plain_password: str) -> str:
    """
    Hash user's plain text password using bcrypt.

    Args:
        plain_password (str): The plain text password entered by the user during registration.
    Returns:
        str: password in a string format.
    """
    password_bytes = plain_password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password_bytes, salt)
    return hashed_password.decode("utf-8")


def check_password(plain_password: str, password_hash: str) -> bool:
    """
    Compare a stored password hash with a user-provided password.

    Args:
        plain_password (str): The plain text password entered by the user during login.
        password_hash (str): The hashed password retrieved from the database.
    Returns:
        bool: True if the passwords match, False otherwise.
    """

    if not (password_hash and plain_password):
        return False
    return bcrypt.checkpw(plain_password.encode("utf-8"), password_hash.encode("utf-8"))


def authenticate_user(email: str, plain_password: str) -> dict | None:
    """
    Authenticate a user by email and password.

    Args:
         email (str): The user's email address (case-insensitive).
         plain_password (str): The user's plaintext password to verify.
     Returns:
         dict | None: The user dict from the database if credentials are correct, otherwise None.
    """

    if not (email and plain_password):
        return None

    user = get_user_by_email(email)

    if not user:
        return None

    if not (check_password(plain_password, user["password_hash"])):
        return None
    return user


def get_user_by_email(email: str) -> dict | None:
    """
    Find a user by their email address from the users table.

    Args:
        email (str): The email address to search for (case-insensitive).
    Returns:
        dict | None: The matching user dictionary if found, otherwise None.
    """

    if not email:
        return None

    email = email.strip().lower()

    try:
        conn = get_db()
        cur = conn.cursor()

        cur.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = cur.fetchone()
        conn.close()

        return user

    except (Exception, sqlite3.Error):
        return None


def get_user_by_id(user_id: int) -> dict | None:
    """
    Find a user by id from the users table.

    Args:
        user_id (int): The user id to search for.
    Returns:
        dict | None: The matching user dictionary if found, otherwise None.
    """

    if not user_id:
        return None

    try:
        conn = get_db()
        cur = conn.cursor()

        cur.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user = cur.fetchone()
        conn.close()

        return user

    except (Exception, sqlite3.Error):
        return None
