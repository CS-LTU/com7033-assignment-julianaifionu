import os
import base64
import re
import hashlib
from dotenv import load_dotenv
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# Load env variables
load_dotenv()


def _derive_key_from_env(env_key_name="STROKE_APP_SECRET_KEY"):
    """
    Accepts either:
      a 64-character hex string (32 bytes)
      any other string but hashed with SHA-256 to 32 bytes
    Raises ValueError if key missing.
    """
    key_raw = os.getenv(env_key_name)
    if not key_raw:
        raise ValueError(f"{env_key_name} not set in environment")

    # If hex string convert to bytes
    if re.fullmatch(r"[0-9a-fA-F]{64}", key_raw):
        return bytes.fromhex(key_raw)

    # Otherwise fallback to sha256(key_raw) to produce 32 bytes
    return hashlib.sha256(key_raw.encode("utf-8")).digest()


# Module-level SECRET_KEY derived from app secret key
SECRET_KEY = _derive_key_from_env()


def encrypt_value(value):
    """
    AES-256-GCM encrypt a string value.
    Returns a dict with base64 iv and base64 ciphertext.
    """
    if value is None:
        return None
    aes = AESGCM(SECRET_KEY)
    iv = os.urandom(12)
    ct = aes.encrypt(iv, value.encode("utf-8"), None)
    return {
        "iv": base64.b64encode(iv).decode("utf-8"),
        "ct": base64.b64encode(ct).decode("utf-8"),
        "alg": "AES-256-GCM",
    }


def decrypt_value(enc_obj):
    """
    Decrypt dict produced by encrypt_value. Returns plaintext string.
    """
    if not enc_obj:
        return None
    try:
        aes = AESGCM(SECRET_KEY)
        iv = base64.b64decode(enc_obj["iv"])
        ct = base64.b64decode(enc_obj["ct"])
        pt = aes.decrypt(iv, ct, None)
        return pt.decode("utf-8")
    except Exception as e:
        raise ValueError("Decryption failed") from e
