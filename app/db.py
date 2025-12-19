import sqlite3
from pathlib import Path

#PROJECT_ROOT = Path(__file__).resolve().parent[1]

# Define the directory where the database file will be stored
DATA_DIR = Path('DATA')

# Define the full path to the SQLite database file
DB_PATH = DATA_DIR / "intelligence_platform.db"

# Used to create a connection if it does not exist
conn = sqlite3.connect(DB_PATH)










