import secrets
import hashlib
from datetime import datetime, timedelta, timezone
from models.auth.auth import hash_password
from models.db_sqlite import get_db
from utils.time_formatter import utc_now


def hash_token(raw_token: str) -> str:
    # Hash the activation token (so raw token is never stored in DB).
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()


def generate_activation_token(user_id: int, hours_valid: int = 24) -> str:
    """
    Creates a secure, one-time activation token for a user.
    Returns the RAW token (for URL), stores only the hash in SQLite.
    """

    # long safe random token
    raw_token = secrets.token_urlsafe(32)
    token_hash = hash_token(raw_token)

    time = datetime.now(timezone.utc)
    expires_at = time + timedelta(hours=hours_valid)

    conn = get_db()
    cur = conn.cursor()

    # Safely invalidate any stale or unused tokens for this user
    cur.execute(
        """
        UPDATE activation_tokens
        SET used_at = ?
        WHERE user_id = ? AND used_at IS NULL
        """,
        (utc_now(), user_id),
    )

    # Store new token
    cur.execute(
        """
        INSERT INTO activation_tokens (user_id, token_hash, expires_at, used_at, created_at)
        VALUES (?, ?, ?, NULL, ?)
        """,
        (user_id, token_hash, expires_at.isoformat(), utc_now()),
    )

    conn.commit()
    conn.close()

    return raw_token


def get_valid_activation_user(raw_token: str):
    """
    Validate the token and return user_id if valid.
    Otherwise, return None.
    """

    token_hash = hash_token(raw_token)
    time = datetime.now(timezone.utc)

    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT user_id, expires_at, used_at
        FROM activation_tokens
        WHERE token_hash = ?
        ORDER BY id DESC
        LIMIT 1
        """,
        (token_hash,),
    )

    row = cur.fetchone()
    conn.close()

    if not row:
        return None

    user_id = row["user_id"]
    expires_at = datetime.fromisoformat(row["expires_at"])
    used_at = row["used_at"]

    # Token already used
    if used_at is not None:
        return None

    # Token expired
    if time > expires_at:
        return None

    return user_id


def mark_token_used(raw_token: str):
    """
    Mark a token as used (so it cannot be reused).
    Returns the timestamp when the token was marked used.
    """

    token_hash = hash_token(raw_token)
    used_at = utc_now()

    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        """
        UPDATE activation_tokens
        SET used_at = ?
        WHERE token_hash = ? AND used_at IS NULL
        """,
        (used_at, token_hash),
    )

    conn.commit()
    conn.close()

    return used_at


def update_user_activation(user_id, new_password, db=None):
    # Update user's password, activate the account, and set updated timestamp
    conn = db or get_db()
    cur = conn.cursor()

    password_hash = hash_password(new_password)
    time = utc_now()

    cur.execute(
        """
        UPDATE users
        SET password_hash = ?, is_active = ?, updated_at = ?
        WHERE id = ?
        """,
        (password_hash, 1, time, user_id),
    )

    conn.commit()
    if db is None:
        conn.close()
