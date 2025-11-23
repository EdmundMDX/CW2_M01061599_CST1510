
import pandas as pd
from app.data.db import connect_database, DATA_DIR




def insert_datasets_metadata(dataset_id, name, rows, columns, uploaded_by, upload_date):
    """Insert a metadata dataset based on the CSV schema."""
    conn = connect_database()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO datasets_metadata 
        (dataset_id, name, rows, columns, uploaded_by, upload_date)
        VALUES (?, ?, ?, ?, ?, ?,?)
    """, (dataset_id, name, rows, columns, uploaded_by, upload_date))

    conn.commit()
    conn.close()

    return dataset_id



def migrate_all_metadata(filepath=DATA_DIR / "datasets_metadata.csv"):
    if not filepath.exists():
        print(f"File not found: {filepath}")
        print("   No incidents to migrate.")
        return

    conn = connect_database()
    
    try:
        metadata_data = pd.read_csv(filepath)
        num_rows = metadata_data.shape[0]
        metadata_data.to_sql('metadata',conn,if_exists='append',index=False)
        print(f"Migrated {num_rows} datasets_metadata from {filepath.name}")
    
    except Exception as e:
        print(f"Error migrating incidents: {e}")
    
    finally:
        conn.close()

    
    
def get_all_metadata():
    """Get all incidents as DataFrame."""
    conn = connect_database()
    df = pd.read_sql_query(
        "SELECT * FROM metadata",
        conn
    )
    conn.close()
    return df