##Purpose**: All functions for managing cyber incidents

import pandas as pd
#from app.db import DATA_DIR
import sqlite3

# CREATE / Insert
def insert_incident(conn, incident_id, timestamp, severity, category, status, description):
    """Insert a new cyber incident based on the CSV schema."""
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO cyber_incidents 
        (incident_id, timestamp, severity, category, status, description)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (incident_id, timestamp, severity, category, status, description))

    conn.commit()
    conn.close()

    return incident_id

#def migrate_all_incidents(conn, filepath=DATA_DIR / "cyber_incidents.csv"):
 #  if not filepath.exists():
#print(f"File not found: {filepath}")
#print("   No incidents to migrate.")
#return

    
    
#try:
#        cyber_incidents_data = pd.read_csv(filepath)
 #       num_rows = cyber_incidents_data.shape[0]
  #      cyber_incidents_data.to_sql('cyber_incidents',conn,if_exists='append',index=False)
   #     print(f"Migrated {num_rows} cyber_incidents from {filepath.name}")
    
#    except Exception as e:
    #    print(f"Error migrating incidents: {e}")
    
    #finally:
     #   conn.close()
    
# READ
def get_all_incidents(conn):
    """Get all incidents as DataFrame."""

    df = pd.read_sql_query(
        "SELECT * FROM cyber_incidents",
        conn
    )
    conn.close()
    return df

# UPDATE
def update_incident_status(conn, incident_id, new_status):
    """ Update the status of an incident.  """
    cursor = conn.cursor()


    update_query = "UPDATE cyber_incidents SET status = ? WHERE incidents_id = ?"
    cursor.execute(update_query, (new_status, incident_id))

    if cursor.rowcount > 0:
        conn.commit()
        print(f"Updated status for incident ID {incident_id} to '{new_status}'.")
    
        cursor.execute("SELECT * FROM cyber_incidents WHERE incident_id = ?", (incident_id,))
        update_record = cursor.fetchone()
        print(f"Updated record details: {update_record}")
    else:
        print(f"Warning: No incident found with ID {incident_id}.")
    conn.close()

# DELETE
def delete_incident(conn, incident_id):
    """Delete an incident from the database"""
    cursor = conn.cursor()

    # Define the DELETE query
    delete_query = "DELETE FROM cyber_incidents WHERE incident_id = ?"
        
    # Execute the query
    cursor.execute(delete_query, (incident_id,))
        
    rows_deleted = cursor.rowcount
    
     # 5. Commit the changes
    if rows_deleted > 0:
        conn.commit()
        print(f"Successfully deleted {rows_deleted} incident(s) with ID: {incident_id}")
    else:
        print(f"No incident found with ID: {incident_id}. Nothing deleted.")
            
     # 6. Ensure the connection is closed
    if conn:
        conn.close()




    # Part 8 . Analytical Queries (The Big 6)
