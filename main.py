# Purpose**: Demonstrate all functionality


from app.data.db import connect_database
from app.data.schema import create_all_tables, create_it_tickets_table
from app.services.user_service import register_user, login_user, migrate_users_from_file
from app.data.incidents import insert_incident, get_all_incidents, migrate_all_incidents
from app.data.metadata import  migrate_all_metadata, get_all_metadata
from app.data.it_tickets import  migrate_it_tickets, get_all_it_tickets

def main():
    print("=" * 60)
    print("Week 8: Database Demo")
    print("=" * 60)

    '''
    # 1. Setup database
    conn = connect_database()
    create_all_tables(conn)
    conn.close()
    
    # 2. Migrate users
    migrate_users_from_file(conn)
    
    # 3. Test authentication
    success, msg = register_user("alice", "SecurePass123!", "analyst")
    print(msg)
    
    success, msg = login_user("alice", "SecurePass123!")
    print(msg)
    
    # 4. Test CRUD
    incident_id = insert_incident(
    2001,
    "00:00.0",
    "High",
    "Phishing",
    "Open",
    "Suspicious email detected")

    print(f"Created incident #{incident_id}")
    '''
    
    # 5. Query data
    df_incidents = get_all_incidents()
    print(f"Total incidents: {len(df_incidents)}")
    
    print('-' * 60)
    df_metadat = get_all_metadata()
    print(f"Total metadata informations: {len(df_metadat)}")

    print('-' * 60)
    df_it_tickets = get_all_it_tickets()
    print(f"Total it tickets: {len(df_it_tickets)}")

    print("=" * 60)
    

if __name__ == "__main__":
    main()