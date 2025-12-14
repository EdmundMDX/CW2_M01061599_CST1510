import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta


# --- Configuration ---
DB_FILE = "intelligence_platform.db" # Using the same database file
TABLE_NAME = "it_tickets"

# Define options for the input formS
TICKET_PRIORITIES = ['Low', 'Medium', 'High', 'Critical']
TICKET_STATUSES = ['Open', 'In Progress', 'Resolved', 'Closed']
ASSIGNED_USERS = ['IT_Support_A', 'IT_Support_B', 'IT_Support_C']


# Database Functions 

def get_db_connection():
    """Establishes and returns the SQLite database connection."""
    try:
        conn = sqlite3.connect(DB_FILE)
        return conn
    except sqlite3.Error as e:
        st.error(f"Error connecting to database: {e}")
        return None

def fetch_ticket_data(table):
    """Fetches all data and returns it as a Pandas DataFrame."""
    conn = get_db_connection()
    if conn:
        try:
            query = f"SELECT * FROM {table}"
            df = pd.read_sql_query(query, conn)
            
            # Ensure the created_at column is ready for charting/display
            if 'created_at' in df.columns:
                df['created_at'] = pd.to_datetime(df['created_at'], errors='coerce')
                
                # Convert date format for display purposes (dd/mm/yy)
                df['Display_Date'] = df['created_at'].dt.strftime('%d/%m/%y')
                
            return df
        except pd.io.sql.DatabaseError as e:
            st.error(f"Error fetching data: {e}")
            return pd.DataFrame()
    return pd.DataFrame()

def add_new_ticket(ticket_id, priority, description, status, assigned_to, created_at, resolution_time_hours):
    """Inserts a new ticket record into the database."""
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            # The table must exist with these columns for this to work.
            insert_query = f"""
            INSERT INTO {TABLE_NAME} (ticket_id, priority, description, status, assigned_to, created_at, resolution_time_hours)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            cursor.execute(insert_query, (ticket_id, priority, description, status, assigned_to, created_at, resolution_time_hours))
            conn.commit()
            st.success("✅ New IT Ticket Recorded Successfully! **Please refresh the page to update the dashboard.**")
        except sqlite3.IntegrityError as e:
            st.error(f"❌ Error: Ticket ID **{ticket_id}** may already exist. {e}")
        except sqlite3.Error as e:
            st.error(f"❌ Error adding ticket: {e}")

# Update function for ticket status and resolution time
def update_ticket_status_and_resolution(ticket_id, new_status, new_resolution_time):
    """Updates the status and resolution time of an existing ticket record."""
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            update_query = f"""
            UPDATE {TABLE_NAME} SET status = ?, resolution_time_hours = ? WHERE ticket_id = ?
            """
            cursor.execute(update_query, (new_status, new_resolution_time, ticket_id))
            conn.commit()

            if cursor.rowcount > 0:
                st.success(f"✏️ Status and Resolution Time for Ticket **{ticket_id}** updated. **Please refresh the page to update the dashboard.**")
            else:
                st.warning(f"⚠️ Ticket ID **{ticket_id}** not found. Update was not performed.")

        except sqlite3.Error as e:
            st.error(f"❌ Error updating ticket: {e}")

def delete_ticket(ticket_id):
    """Deletes a ticket record based on the ticket_id."""
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            delete_query = f"""
            DELETE FROM {TABLE_NAME} WHERE ticket_id = ?
            """
            cursor.execute(delete_query, (ticket_id,))
            conn.commit()

            # Check how many rows were affected
            if cursor.rowcount > 0:
                st.success(f"🗑️ Ticket **{ticket_id}** successfully deleted. **Please refresh the page to update the dashboard.**")
            else:
                st.warning(f"⚠️ Ticket ID **{ticket_id}** not found in the database.")

        except sqlite3.Error as e:
            st.error(f"❌ Error deleting ticket: {e}")


# Streamlit Layout

st.set_page_config(layout="wide", page_title="IT Ticket Dashboard")
st.title("👨‍💻 IT Ticket Dashboard")

# Ensure state keys exist (in case user opens this page first)
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

# Guard: if not logged in, send user back
if not st.session_state.logged_in:
    st.error("You must be logged in to view the dashboard.")
    if st.button("Go to login page"):
        st.switch_page("Home.py")   # back to the first page
    st.stop()

# Create main tabs for the interface
tab_dashboard, tab_add_ticket, tab_update_ticket, tab_delete_ticket = st.tabs([
    "📊 Dashboard",
    "➕ New Ticket",
    "✏️ Update Ticket Status/Resolution",
    "🗑️ Delete Ticket"
])

# Dashboard Overview
with tab_dashboard:
    st.header("Ticket Summary")

    data_df = fetch_ticket_data(TABLE_NAME)

    if not data_df.empty:

        # Key Metrics 
        total = len(data_df)
        # Sum resolution time only for tickets that have a value
        total_resolution = data_df['resolution_time_hours'].sum() if 'resolution_time_hours' in data_df.columns and not data_df['resolution_time_hours'].empty else 0
        
        # Calculate tickets created today
        today = datetime.now().date()
        if 'created_at' in data_df.columns:
            # Filter for dates that match today's date
            created_today = data_df[data_df['created_at'].dt.date == today].shape[0]
        else:
            created_today = 0


        col_total, col_resolution, col_today = st.columns(3)
        col_total.metric("Total Tickets", total)
        # Format resolution time to one decimal place
        col_resolution.metric("Total Resolution Time (Hours)", f"{total_resolution:,.1f}") 
        col_today.metric("Created Today", created_today)

        st.markdown("---")

        # --- Charts ---
        col_chart_1, col_chart_2 = st.columns(2)

        # Chart 1: Status Distribution
        with col_chart_1:
            if 'status' in data_df.columns:
                st.subheader("Ticket Status Distribution")
                status_counts = data_df['status'].value_counts().reset_index()
                status_counts.columns = ['Status', 'Count']
                fig_status = px.pie(
                    status_counts, 
                    names='Status', 
                    values='Count', 
                    title='Distribution by Status',
                    hole=.3 # Makes it a donut chart
                )
                st.plotly_chart(fig_status, use_container_width=True)

        # Chart 2: Priority Distribution
        with col_chart_2:
            if 'priority' in data_df.columns:
                st.subheader("Ticket Priority Distribution")
                priority_order = TICKET_PRIORITIES # Use the defined order for consistency
                # Ensure all defined priorities are present in the chart, even with 0 counts
                priority_counts = data_df['priority'].value_counts().reindex(priority_order, fill_value=0).reset_index()
                priority_counts.columns = ['Priority', 'Count']
                
                fig_priority = px.bar(
                    priority_counts,
                    x='Priority',
                    y='Count',
                    color='Priority', # Color intensity based on column count
                    category_orders={"Priority": priority_order}, # Enforce defined order
                    title='Count by Priority Level',
                    labels={'Priority': 'Priority Level', 'Count': 'Number of Tickets'}
                )
                st.plotly_chart(fig_priority, use_container_width=True)
            elif data_df.empty:
                st.subheader("Ticket Priority Distribution")
                st.info("Add data to view this chart.")

        st.markdown("---")

        # Raw Data Table 
        st.subheader("Raw Ticket Data")
        
        # Select and rename columns for display
        display_cols = ['ticket_id', 'priority', 'description', 'status', 'assigned_to', 'resolution_time_hours', 'Display_Date']
        
        # Create a dictionary to rename the 'Display_Date' column to 'created_at' for the UI
        rename_map = {'Display_Date': 'created_at'}
        
        # Select the columns, sort, and rename 'Display_Date' back to 'created_at' for user view
        data_to_display = data_df[display_cols].sort_values(by='ticket_id', ascending=True).rename(columns=rename_map)
        
        # Format resolution_time_hours for display
        data_to_display['resolution_time_hours'] = data_to_display['resolution_time_hours'].round(1)

        st.dataframe(data_to_display, use_container_width=True)

    else:
        st.warning(f"No data available in the '{TABLE_NAME}' table. Use the 'New Ticket' tab to add records.")

# Add New Ticket
with tab_add_ticket:
    st.header("Add New IT Ticket Record")

    with st.form("ticket_form"):

        col_id, col_priority = st.columns(2)
        ticket_id = col_id.text_input("1. Ticket ID (e.g., 2007)", placeholder="1000")
        priority = col_priority.selectbox("2. Priority", TICKET_PRIORITIES)

        description = st.text_area("3. Description", placeholder="User cannot log in to the main application.")

        col_status, col_assigned = st.columns(2)
        status = col_status.selectbox("4. Status", TICKET_STATUSES, index=0) # Default to 'Open'
        assigned_to = col_assigned.selectbox("5. Assigned To", ASSIGNED_USERS)

        col_date, col_resolution = st.columns(2)
        # Date/Time handling: Use a datetime input for better date control
        now = datetime.now()
        created_at_dt = col_date.date_input("6. Creation Date", now.date())
        # Combine date and time for the database string (still yyyy-mm-dd for SQLite)
        created_at_full = f"{created_at_dt}"
        
        # Resolution time only required if status is not Open/In Progress
        if status in ['Resolved', 'Closed']:
            resolution_time_hours_str = col_resolution.text_input("7. Resolution Time (Hours)", value="0.5")
        else:
            # Set to 0 if not resolved/closed
            resolution_time_hours_str = col_resolution.text_input("7. Resolution Time (Hours)", value="0.0", disabled=True) 

        submitted = st.form_submit_button("Submit New Ticket")

        if submitted:
            # Input validation and type conversion
            if ticket_id.strip() and description.strip():
                try:
                    # Convert resolution time input to float
                    resolution_time_float = float(resolution_time_hours_str)

                    add_new_ticket(
                        ticket_id.strip(),
                        priority,
                        description.strip(),
                        status,
                        assigned_to,
                        created_at_full,
                        resolution_time_float
                    )
                except ValueError:
                    st.error("Resolution Time must be a valid number (e.g., 0.5, 2.0).")

            else:
                st.error("Ticket ID and Description are required fields.")

# Update Ticket Status/Resolution
with tab_update_ticket:
    st.header("Update Ticket Status and Resolution Time")
    st.info("💡 You can find the **Ticket ID** in the **Dashboard** tab's **Raw Ticket Data** table.")

    with st.form("update_ticket_form"):

        update_id = st.text_input("1. Enter Ticket ID to Update", placeholder="e.g., 1000")
        
        col_status, col_resolution = st.columns(2)
        new_status = col_status.selectbox("2. New Status", TICKET_STATUSES, index=TICKET_STATUSES.index('In Progress'))
        new_resolution_time_str = col_resolution.text_input("3. New Resolution Time (Hours)", placeholder="e.g., 1.5")
        
        update_submitted = st.form_submit_button("Update Ticket", type="primary")

        if update_submitted:
            if update_id.strip() and new_resolution_time_str.strip():
                try:
                    new_resolution_time_float = float(new_resolution_time_str)
                    update_ticket_status_and_resolution(
                        update_id.strip(), 
                        new_status, 
                        new_resolution_time_float
                    )
                except ValueError:
                    st.error("Resolution Time must be a valid number (e.g., 0.5, 2.0).")
            else:
                st.error("Please enter a valid Ticket ID, Status, and Resolution Time.")

# Delete Ticket
with tab_delete_ticket:
    st.header("Delete Ticket Record")
    st.warning("🚨 **Warning:** This action is permanent and cannot be undone.")

    with st.form("delete_form"):
        # Text input to get the ID to delete
        delete_id = st.text_input("Enter Ticket ID to Delete", placeholder="e.g., 1001")

        # Submission button for the delete operation
        delete_submitted = st.form_submit_button("Delete Record", type="primary")

        if delete_submitted:
            if delete_id.strip():
                delete_ticket(delete_id.strip())
            else:
                st.error("Please enter a valid Ticket ID.")

# Logout button
st.divider()
if st.button("Log out"):
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.info("You have been logged out.")
    st.switch_page("Home.py")