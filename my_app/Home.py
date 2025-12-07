import streamlit as st
import sqlite3
import bcrypt 

# --- Configuration ---
DB_FILE = "intelligence_platform.db"
TABLE_NAME = "users"

st.set_page_config(page_title="Login / Register", page_icon="🔑", layout="centered")

# 🔐 DATABASE AND AUTHENTICATION FUNCTIONS

def init_db():
    """Ensure the users table exists with the correct columns."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(f"""
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
            username TEXT PRIMARY KEY,
            password_hash TEXT
        )
    """)
    conn.commit()
    conn.close()

def fetch_user_hash(username):
    """Fetches a user's password hash from the database."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(f"SELECT password_hash FROM {TABLE_NAME} WHERE username = ?", (username,))
    result = c.fetchone()
    conn.close()
    
    # If the user doesn't exist, this line will crash the app with a TypeError (result[0] on None)
    return result[0]


def register_user(username, password):
    """Hashes a password and inserts the new user into the database."""
    
    password_bytes = password.encode('utf-8')
    hashed_password = bcrypt.hashpw(password_bytes, bcrypt.gensalt())

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(f"INSERT INTO {TABLE_NAME} (username, password_hash) VALUES (?, ?)",
              (username, hashed_password.decode('utf-8')))
    conn.commit()
    conn.close()
    
    return True 

# Initialize the database structure 
init_db()

# 💻 STREAMLIT APP LOGIC 

# Initialise session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""

st.title("🔐 Welcome")

# If already logged in, go straight to dashboard
if st.session_state.logged_in:
    st.success(f"Already logged in as **{st.session_state.username}**.")
    if st.button("Go to dashboard"):
        st.switch_page("pages/1_IT_Tickets.py")
    st.stop()

# ---------- Tabs: Login / Register ----------
tab_login, tab_register = st.tabs(["Login", "Register"])

# ----- LOGIN TAB -----
with tab_login:
    st.subheader("Login")

    login_username = st.text_input("Username", key="login_username")
    login_password = st.text_input("Password", type="password", key="login_password")

    if st.button("Log in", type="primary"):
        # 1. Fetch the stored hash from the database
        stored_hash_str = fetch_user_hash(login_username) 

        # 2. Compare the entered password with the stored hash using bcrypt
        entered_password_bytes = login_password.encode('utf-8')
        stored_hash_bytes = stored_hash_str.encode('utf-8')

        # bcrypt.checkpw safely compares the password against the hash
        if bcrypt.checkpw(entered_password_bytes, stored_hash_bytes):
            # Login successful
            st.session_state.logged_in = True
            st.session_state.username = login_username
            st.success(f"Welcome back, {login_username}! ")
            st.switch_page("pages/1_IT_Tickets.py")
        

# ----- REGISTER TAB -----
with tab_register:
    st.subheader("Register")

    new_username = st.text_input("Choose a username", key="register_username")
    new_password = st.text_input("Choose a password", type="password", key="register_password")
    confirm_password = st.text_input("Confirm password", type="password", key="register_confirm")

    if st.button("Create account"):
        
        register_user(new_username, new_password)
        st.success("Account created! You can now log in from the Login tab.")
        st.info("Tip: go to the Login tab and sign in with your new account.")