
import pandas as pd
# from app.db import connect_database, DATA_DIR
import sqlite3



# Insert data
def insert_datasets_metadata(conn, dataset_id, name, rows, columns, uploaded_by, upload_date):
    """Insert a metadata dataset based on the CSV schema."""
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO metadata 
        (dataset_id, name, rows, columns, uploaded_by, upload_date)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (dataset_id, name, rows, columns, uploaded_by, upload_date))

    conn.commit()
    conn.close()

    return dataset_id



''' migrate data from csv
def migrate_all_metadata(conn, filepath=DATA_DIR / "datasets_metadata.csv"):
    if not filepath.exists():
        print(f"File not found: {filepath}")
        print("   No incidents to migrate.")
        return

    
    try:
        metadata_data = pd.read_csv(filepath)
        num_rows = metadata_data.shape[0]
        metadata_data.to_sql('metadata',conn,if_exists='append',index=False)
        print(f"Migrated {num_rows} datasets_metadata from {filepath.name}")
    
    except Exception as e:
        print(f"Error migrating incidents: {e}")
    
    finally:
        conn.close()
'''
    
   # read all data 
def get_all_metadata(conn):
    """Get all datasets as DataFrame."""
    df = pd.read_sql_query(
        "SELECT * FROM metadata",
        conn
    )
    conn.close()
    return df

# UPDATE
def update_dataset_name(conn, dataset_id, new_name):
    """ Update the name of an dataset.  """
    cursor = conn.cursor()


    update_query = "UPDATE metadata SET name = ? WHERE dataset_id = ?"
    cursor.execute(update_query, (new_name, dataset_id))

    if cursor.rowcount > 0:
        conn.commit()
        print(f"Updated name for dataset ID {dataset_id} to '{new_name}'.")
    
        cursor.execute("SELECT * FROM metadata WHERE dataset_id = ?", (dataset_id,))
        update_record = cursor.fetchone()
        print(f"Updated record details: {update_record}")
    else:
        print(f"Warning: No dataset ID found with ID {dataset_id}.")
    conn.close()



# DELETE
def delete_dataset(conn, dataset_id):
    """Delete a dataset from the database"""
    cursor = conn.cursor()

    # Define the DELETE query
    delete_query = "DELETE FROM metadata WHERE dataset_id = ?"
        
    # Execute the query
    cursor.execute(delete_query, (dataset_id,))
        
    rows_deleted = cursor.rowcount
    
     # 5. Commit the changes
    if rows_deleted > 0:
        conn.commit()
        print(f"Successfully deleted {rows_deleted} dataset with ID: {dataset_id}")
    else:
        print(f"No dataset found with ID: {dataset_id}. Nothing deleted.")
            
     # 6. Ensure the connection is closed
    if conn:
        conn.close()

