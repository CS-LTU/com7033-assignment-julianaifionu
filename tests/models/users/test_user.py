import pytest
from models.users.user_model import create_user


def test_create_user_success(sqlite_test_db):
    # Test that create_user successfully adds a new user and that the username matches the expected value
    user_id = create_user("hana", "Hana Doe", "admin", db=sqlite_test_db)
    cur = sqlite_test_db.cursor()
    cur.execute("SELECT * FROM users WHERE id=?", (user_id,))
    user = cur.fetchone()
    assert user["username"] == "hana"


def test_create_user_invalid_role(sqlite_test_db):
    # Test that create_user raises ValueError if the role does not exist.
    with pytest.raises(ValueError) as exc:
        create_user("janedoe", "Jane Doe", "nonexistent_role", db=sqlite_test_db)

    assert "Role 'nonexistent_role' does not exist." in str(exc.value)
