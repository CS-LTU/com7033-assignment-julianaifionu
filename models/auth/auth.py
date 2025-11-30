import bcrypt
from models.db_sqlite import get_db
from utils.time_formatter import utc_now

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


def verify_password(plain_password: str, password_hash: str) -> bool:
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


def authenticate_user(username: str, plain_password: str) -> dict | None:
    """
    Authenticate a user by username and password.

    Args:
         username (str): The user's username.
         plain_password (str): The user's plaintext password to verify.
     Returns:
         dict | None: The user dict from the database if credentials are correct, otherwise None.
    """

    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cur.fetchone()
    conn.close()

    if not user:
        return None

    if not user["is_active"]:
        return None
    
    if not user["password_hash"]:
        return None

    if not (verify_password(plain_password, user["password_hash"])):
        return None
    return user


def get_user_by_username(username: str) -> dict | None:
    """
    Find a user by their username.

    Args:
        username (str): The username to search for.
    Returns:
        dict | None: The matching user dictionary if found, otherwise None.
    """

    if not username:
        return None

    username = username.strip()
    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT users.*, roles.name AS role_name
        FROM users
        JOIN roles ON users.role_id = roles.id
        WHERE users.username = ?
        """,
        (username,),
    )

    row = cur.fetchone()
    conn.close()
    return row


def get_user_by_id(user_id: int) -> dict | None:
    """
    Find a user by id.

    Args:
        user_id (int): The user id to search for.
    Returns:
        dict | None: The matching user dictionary if found, otherwise None.
    """

    if not user_id:
        return None

    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT users.*, roles.name AS role_name
        FROM users
        JOIN roles ON users.role_id = roles.id
        WHERE users.id = ?
        """,
        (user_id,),
    )

    row = cur.fetchone()
    conn.close()
    return row



