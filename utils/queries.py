from utils.db_sqlite import get_db
from utils.auth import hash_password


def create_user(first_name, last_name, email, role, temp_password):
    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO users 
        (first_name, last_name, email, password_hash, role)
        VALUES (?, ?, ?, ?, ?)
        """,
        (first_name, last_name, email, hash_password(temp_password), role),
    )

    new_user_id = cur.lastrowid
    
    conn.commit()
    conn.close()

    return new_user_id


def update_user_activation(user_id, new_password):
    conn = get_db()
    cur = conn.cursor()

    password_hash = hash_password(new_password)

    cur.execute(
        """
        UPDATE users
        SET password_hash = ?, is_active = ?
        WHERE id = ?
        """,
        (password_hash, True, user_id),
    )

    conn.commit()
    conn.close()
