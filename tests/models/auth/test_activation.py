from models.users.user_model import create_user
from models.auth.activation import update_user_activation


def test_update_user_activation(sqlite_test_db):
    # Test updating a user's password and activation status.
    cur = sqlite_test_db.cursor()

    # Create user
    user_id = create_user("johndoe", "John Doe", "admin", db=sqlite_test_db)
    new_password = "StrongP@ssw0rd1"
    update_user_activation(user_id, new_password, db=sqlite_test_db)

    # Verify update
    cur.execute("SELECT * FROM users WHERE id=?", (user_id,))
    user = cur.fetchone()

    assert user is not None
    assert user["is_active"] == 1
