import streamlit as st
import sqlite3
import bcrypt

# --- Configuration ---
DB_FILE = "intelligence_platform.db"
TABLE_NAME = "users"

st.set_page_config(page_title="Login / Register", page_icon="🔑", layout="centered")


# -------------------- DATA LAYER --------------------
class UserRepository:
    def __init__(self, db_file=DB_FILE):
        self.db_file = db_file
        self._init_db()

    def _connect(self):
        return sqlite3.connect(self.db_file)

    def _init_db(self):
        with self._connect() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    username TEXT PRIMARY KEY,
                    password_hash TEXT
                )
            """)
            conn.commit()

    def get_user_hash(self, username):
        with self._connect() as conn:
            cur = conn.execute(
                "SELECT password_hash FROM users WHERE username = ?",
                (username,),
            )
            row = cur.fetchone()
        return row[0] if row else None

    def create_user(self, username, password_hash):
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                (username, password_hash),
            )
            conn.commit()


# -------------------- AUTH LOGIC --------------------
class AuthService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    @staticmethod
    def _hash_password(password: str) -> str:
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    @staticmethod
    def _check_password(password: str, stored_hash: str) -> bool:
        return bcrypt.checkpw(password.encode(), stored_hash.encode())

    def login(self, username, password):
        stored_hash = self.repo.get_user_hash(username)
        if not stored_hash:
            return False, "User not found."

        if not self._check_password(password, stored_hash):
            return False, "Incorrect password."

        return True, "Login successful."

    def register(self, username, password):
        if self.repo.get_user_hash(username):
            return False, "Username already exists."

        password_hash = self._hash_password(password)
        self.repo.create_user(username, password_hash)
        return True, "Account created."


# -------------------- STREAMLIT UI --------------------
class LoginApp:
    def __init__(self, auth: AuthService):
        self.auth = auth
        self._init_session()

    def _init_session(self):
        st.session_state.setdefault("logged_in", False)
        st.session_state.setdefault("username", "")

    def run(self):
        st.title("🔐 Welcome")

        if st.session_state.logged_in:
            st.success(f"Logged in as **{st.session_state.username}**")
            if st.button("Go to dashboard"):
                st.switch_page("pages/1_IT_Tickets.py")  # ✅ original link
            st.stop()

        login_tab, register_tab = st.tabs(["Login", "Register"])
        with login_tab:
            self.login_tab()
        with register_tab:
            self.register_tab()

    def login_tab(self):
        st.subheader("Login")
        username = st.text_input("Username", key="login_user")
        password = st.text_input("Password", type="password", key="login_pass")

        if st.button("Log in", type="primary"):
            ok, msg = self.auth.login(username.strip(), password)
            if ok:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success(msg)
                st.switch_page("pages/1_IT_Tickets.py")  # ✅ original link
            else:
                st.error(msg)

    def register_tab(self):
        st.subheader("Register")
        username = st.text_input("Choose a username", key="reg_user")
        password = st.text_input("Choose a password", type="password", key="reg_pass")
        confirm = st.text_input("Confirm password", type="password", key="reg_confirm")

        if st.button("Create account"):
            if password != confirm:
                st.error("Passwords do not match.")
                return

            ok, msg = self.auth.register(username.strip(), password)
            if ok:
                st.success(msg)
                st.info("You can now log in from the Login tab.")
            else:
                st.error(msg)


# -------------------- APP BOOTSTRAP --------------------
repo = UserRepository()
auth = AuthService(repo)
LoginApp(auth).run()
