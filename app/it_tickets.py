
import pandas as pd
# from app.db import connect_database, DATA_DIR
import sqlite3



# Insert
def insert_it_tickets(conn, ticket_id, priority, description, status, assigned_to, created_at, resolution_time_hours):
    """Insert a new it ticket based on the CSV schema."""
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO it_tickets 
        (ticket_id, priority, description, status, assigned_to, created_at, resolution_time_hours)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (ticket_id, priority, description, status, assigned_to, created_at, resolution_time_hours))

    conn.commit()
    conn.close()

    return ticket_id

'''
def migrate_it_tickets(conn, filepath=DATA_DIR / "it_tickets.csv"):
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
'''
    
    
def get_all_it_tickets(conn):
    """Get all tickets as DataFrame."""
    df = pd.read_sql_query(
        "SELECT * FROM it_tickets",
        conn
    )
    conn.close()
    return df

# UPDATE
def update_ticket_status(conn, ticket_id, updated_status):
    """ Update the status of an ticket.  """
    cursor = conn.cursor()


    update_query = "UPDATE it_tickets SET status = ? WHERE ticket_id = ?"
    cursor.execute(update_query, (updated_status, ticket_id))

    if cursor.rowcount > 0:
        conn.commit()
        print(f"Updated status for ticket ID {ticket_id} to '{updated_status}'.")
    
        cursor.execute("SELECT * FROM it_tickets WHERE ticket_id = ?", (ticket_id,))
        update_record = cursor.fetchone()
        print(f"Updated record details: {update_record}")
    else:
        print(f"Warning: No ticket found with ID {ticket_id}.")
    conn.close()


# DELETE
def delete_ticket(conn, ticket_id):
    """Delete an ticket from the database"""
    cursor = conn.cursor()

    # Define the DELETE query
    delete_query = "DELETE FROM it_tickets WHERE ticket_id = ?"
        
    # Execute the query
    cursor.execute(delete_query, (ticket_id,))
        
    rows_deleted = cursor.rowcount
    
     # 5. Commit the changes
    if rows_deleted > 0:
        conn.commit()
        print(f"Successfully deleted {rows_deleted} incident(s) with ID: {ticket_id}")
    else:
        print(f"No incident found with ID: {ticket_id}. Nothing deleted.")
            
     # 6. Ensure the connection is closed
    if conn:
        conn.close()
