import sqlite3

# To migrate all users by username
def get_user_by_username(conn, username):
    """Retrieve user by username."""
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM users WHERE username = ?",
        (username,)
    )
    user = cursor.fetchone()
    conn.close()
    return user

# To insert a new users with details including username, password_password and role user, which are saved on the users table 
def insert_user(conn, username, password_hash, role='user'):
    """Insert new user."""
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
        (username, password_hash, role)
    )
    conn.commit()
    conn.close()

    conn = sqlite3.connect('DATA/intelligence_platform.db')
    insert_user(conn, username="bobby", password_hash="SecurePass123", role='user')
