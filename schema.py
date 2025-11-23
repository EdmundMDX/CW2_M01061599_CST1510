


def create_all_tables(conn):
    """Create all tables."""
    create_users_table(conn)
    create_cyber_incidents_table(conn)
    create_datasets_metadata_table(conn)
    create_it_tickets_table(conn)

def create_users_table(conn):
    """
    Create the users table if it doesn't exist.
    This is a COMPLETE IMPLEMENTATION as an example.
    Study this carefully before implementing the other tables!
    
    Args:
        conn: Database connection object
    """
    cursor = conn.cursor()
    
    # SQL statement to create users table
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        role TEXT DEFAULT 'user',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """
    cursor.execute(create_table_sql)
    conn.commit()
    print("✅ Users table created successfully!")


def create_cyber_incidents_table(conn):
    """
    Create the cyber_incidents table based on the CSV schema.
    
    Args:
        conn: Database connection object
    """
    cursor = conn.cursor()

    create_table_sql = """
    CREATE TABLE IF NOT EXISTS cyber_incidents (
        incident_id INTEGER PRIMARY KEY,
        timestamp TEXT NOT NULL,
        severity TEXT NOT NULL,
        category TEXT NOT NULL,
        status TEXT NOT NULL,
        description TEXT
    );
    """

    cursor.execute(create_table_sql)
    conn.commit()
    print("✅ cyber_incidents table created successfully !")


    # SQL statement to create metadata table

def create_datasets_metadata_table(conn):
    """
    Create the datasets metadata table based on the CSV schema.

    Args:
        conn: Database connection object
    """
    cursor = conn.cursor()

    create_table_sql = """
    CREATE TABLE IF NOT EXISTS metadata (
        dataset_id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        rows INTEGER NOT NULL,
        columns INTEGER NOT NULL,
        uploaded_by TEXT NOT NULL,
        upload_date TEXT NOT NULL
    );
    """

    cursor.execute(create_table_sql)
    conn.commit()
    print("✅ metadata table created successfully !")


def create_it_tickets_table(conn):
    """
    Create the it_tickets table based on the CSV schema.

    Args:
        conn: Database connection object
    """
    cursor = conn.cursor()

    create_table_sql = """
    CREATE TABLE IF NOT EXISTS it_tickets (
        ticket_id INTEGER PRIMARY KEY,
        priority TEXT NOT NULL,
        description TEXT NOT NULL,
        status TEXT NOT NULL,
        assigned_to TEXT NOT NULL,
        created_at TEXT NOT NULL,
        resolution_time_hours INTEGER
    );
    """

    cursor.execute(create_table_sql)
    conn.commit()
    print("✅ it_tickets table created successfully !")
