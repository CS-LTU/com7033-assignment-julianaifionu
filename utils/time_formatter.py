from datetime import datetime, timezone


def utc_now():
    """Returns the current UTC time in ISO 8601 format."""
    return datetime.now(timezone.utc).isoformat()
