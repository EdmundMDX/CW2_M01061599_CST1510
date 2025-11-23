
import pandas as pd
from app.data.db import connect_database, DATA_DIR




def insert_it_tickets(ticket_id, priority, description, status, assigned_to, created_at, resolution_time_hours):
    """Insert a new it ticket based on the CSV schema."""
    conn = connect_database()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO it_tickets 
        (ticket_id, priority, description, status, assigned_to, created_at, resolution_time_hours)
        VALUES (?, ?, ?, ?, ?, ?,?)
    """, (ticket_id, priority, description, status, assigned_to, created_at, resolution_time_hours))

    conn.commit()
    conn.close()

    return ticket_id



def migrate_it_tickets(filepath=DATA_DIR / "it_tickets.csv"):
    if not filepath.exists():
        print(f"File not found: {filepath}")
        print("   No incidents to migrate.")
        return

    conn = connect_database()
    
    try:
        metadata_data = pd.read_csv(filepath)
        num_rows = metadata_data.shape[0]
        metadata_data.to_sql('it_tickets',conn,if_exists='append',index=False)
        print(f"Migrated {num_rows} it_tickets from {filepath.name}")
    
    except Exception as e:
        print(f"Error migrating it_tickets: {e}")
    
    finally:
        conn.close()

    
    
def get_all_it_tickets():
    """Get all incidents as DataFrame."""
    conn = connect_database()
    df = pd.read_sql_query(
        "SELECT * FROM it_tickets",
        conn
    )
    conn.close()
    return df