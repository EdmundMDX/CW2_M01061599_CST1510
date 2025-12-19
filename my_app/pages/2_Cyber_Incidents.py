import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
from datetime import datetime

# Database and table migrated/connected
DB_FILE = "intelligence_platform.db"
TABLE_NAME = "cyber_incidents" 

# Define options for the input form
INCIDENT_SEVERITIES = ['Low', 'Medium', 'High', 'Critical']
INCIDENT_CATEGORIES = ['Malware', 'Phishing', 'Denial of Service', 'Insider Threat', 'Data Breach', 'Vulnerability Scan', 'Other']
INCIDENT_STATUSES = ['Open', 'In Progress', 'Closed', 'Pending Review']

# Database Functions 
def get_db_connection():
    """Establishes and returns the SQLite database connection."""
    try:
        conn = sqlite3.connect(DB_FILE)
        return conn
    except sqlite3.Error as e:
        st.error(f"Error connecting to database: {e}")
        return None


def fetch_incident_data(table):
    """Fetches all data and returns it as a Pandas DataFrame."""
    conn = get_db_connection()
    if conn:
        try:
            query = f"SELECT * FROM {table}" 
            df = pd.read_sql_query(query, conn)
            # Ensure the timestamp column is ready to be displayed
            if 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
            return df
        except pd.io.sql.DatabaseError as e:
            st.error(f"Error fetching data: {e}")
            return pd.DataFrame()
    return pd.DataFrame()

# Add a incident
def add_new_incident(incident_id, timestamp, severity, category, status, description):
    """Inserts a new incident record into the database."""
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            insert_query = f"""
            INSERT INTO {TABLE_NAME} (incident_id, timestamp, severity, category, status, description) 
            VALUES (?, ?, ?, ?, ?, ?)
            """
            cursor.execute(insert_query, (incident_id, timestamp, severity, category, status, description))
            conn.commit()
            st.success("  New Incident Recorded Successfully! **Please refresh the page to update the dashboard.**")
            fetch_incident_data("cyber_incidents")
        except sqlite3.IntegrityError as e:
            st.error(f" Error: Incident ID **{incident_id}** may already exist. {e}")
        except sqlite3.Error as e:
            st.error(f" Error adding incident: {e}")

# Update the status of a chosen incident 
def update_incident_status(incident_id, new_status):
    """Updates the status of an existing incident record."""
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            update_query = f"""
            UPDATE {TABLE_NAME} SET status = ? WHERE incident_id = ?
            """
            cursor.execute(update_query, (new_status, incident_id))
            conn.commit()
            
            if cursor.rowcount > 0:
                st.success(f" Status for Incident **{incident_id}** updated to **{new_status}**. **Please refresh the page to update the dashboard.**")
            else:
                st.warning(f" Incident ID **{incident_id}** not found. Status was not updated.")
                
        except sqlite3.Error as e:
            st.error(f" Error updating incident status: {e}")

# Delete an incident record             
def delete_incident(incident_id):
    """Deletes an incident record based on the incident_id."""
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            delete_query = f"""
            DELETE FROM {TABLE_NAME} WHERE incident_id = ?
            """
            cursor.execute(delete_query, (incident_id,))
            conn.commit()
            
            # Check how many rows were affected
            if cursor.rowcount > 0:
                st.success(f" Incident **{incident_id}** successfully deleted. **Please refresh the page to update the dashboard.**")
                fetch_incident_data("cyber_incidents")
            else:
                st.warning(f" Incident ID **{incident_id}** not found in the database.")
                
        except sqlite3.Error as e:
            st.error(f" Error deleting incident: {e}")


# Streamlit Layout 
st.set_page_config(layout="wide", page_title="Cybersecurity Dashboard") 
st.title("🛡️Cyber Incident Dashboard")

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

# Creating four main tabs to be used for CRUD functions
tab_dashboard, tab_add_incident, tab_update_status, tab_delete_incident = st.tabs([
    "📊 Dashboard", 
    "➕ New Incident", 
    "✏️ Update Status",
    "🗑️ Delete Incident"
])

# Dashboard Overview
with tab_dashboard:
    st.header("Incident Summary")
    
    data_df = fetch_incident_data(TABLE_NAME)

    if not data_df.empty:
        
        # Key Metrics
        total = len(data_df)
        open_count = data_df[data_df['status'].str.lower() == 'open'].shape[0] if 'status' in data_df.columns else 0
        closed_count = total - open_count
        
        col_total, col_open, col_closed = st.columns(3)
        col_total.metric("Total Incidents", total)
        col_open.metric("Currently Open", open_count)
        col_closed.metric("Incidents Closed", closed_count)

        st.markdown("---")
        
        # Charts 
        col_chart_1, col_chart_2 = st.columns(2)

        # Chart 1: Category Distribution
        with col_chart_1:
            if 'category' in data_df.columns:
                st.subheader("Category Distribution")
                category_counts = data_df['category'].value_counts().reset_index()
                category_counts.columns = ['Incident Category', 'Count']
                fig_category = px.bar(category_counts, x='Incident Category', y='Count', title='Count by Incident Category')
                st.plotly_chart(fig_category, use_container_width=True)
            
        # Chart 2: Severity Breakdown
        with col_chart_2:
            if 'severity' in data_df.columns:
                st.subheader("Severity Breakdown")
                severity_order = INCIDENT_SEVERITIES
                severity_counts = data_df['severity'].value_counts().reindex(severity_order).fillna(0).reset_index()
                severity_counts.columns = ['Severity', 'Count']

                fig_severity = px.pie(severity_counts, names='Severity', values='Count', title='Percentage by Severity')
                st.plotly_chart(fig_severity, use_container_width=True)
        
        st.markdown("---")
        
# Raw Data Table 
        st.subheader("Raw Data")
        st.dataframe(data_df.sort_values(by='incident_id', ascending=True), use_container_width=True)
        
    else:
        st.warning(f"No data available in the '{TABLE_NAME}' table. Use the 'New Incident' tab to add records.")

# Add New Incident
with tab_add_incident:
    st.header("Report New Incident")

    with st.form("incident_form"):
        
        description = st.text_area("6. Description", placeholder="Provide detailed summary of the event.")
        
        col_id, col_ts = st.columns(2)
        incident_id = col_id.text_input("1. Incident ID (e.g., 0000)", placeholder="1000")
        
        time_input = col_ts.time_input("2. Time", datetime.now().time()) # Changed to .time() for simplicity
        incident_timestamp = f"{datetime.now().date()} {time_input}" # Combine current date with time input

        col_sev, col_cat, col_status = st.columns(3)
        severity = col_sev.selectbox("3. Severity", INCIDENT_SEVERITIES)
        category = col_cat.selectbox("4. Category", INCIDENT_CATEGORIES)
        status = col_status.selectbox("5. Status", INCIDENT_STATUSES, index=0)

        submitted = st.form_submit_button("Submit Incident")

        if submitted:
            if incident_id.strip() and description.strip():
                add_new_incident(incident_id.strip(), incident_timestamp, severity, category, status, description)
            else:
                st.error("Incident ID and Description are required fields.")

# Update Incident Status
with tab_update_status:
    st.header("Update Incident Status")
    st.info("💡 You can find the **Incident ID** in the **Dashboard** tab's **Raw Data** table.")
    
    with st.form("update_status_form"):
        
        update_id = st.text_input("1. Enter Incident ID to Update", placeholder="e.g., 1000")
        new_status = st.selectbox("2. Select New Status", INCIDENT_STATUSES)
        
        update_submitted = st.form_submit_button("Update Status", type="primary")

        if update_submitted:
            if update_id.strip():
                update_incident_status(update_id.strip(), new_status)
            else:
                st.error("Please enter a valid Incident ID.")

# Delete Incident
with tab_delete_incident:
    st.header("Delete Incident Record")
    st.warning("🚨 **Warning:** This action is permanent and cannot be undone.")

    with st.form("delete_form"):
        # Text input to get the ID to delete
        delete_id = st.text_input("Enter Incident ID to Delete", placeholder="e.g., 1000")
        
        # Submission button for the delete operation
        delete_submitted = st.form_submit_button("Delete Record", type="primary")

        if delete_submitted:
            if delete_id.strip():
                delete_incident(delete_id.strip())
            else:
                st.error("Please enter a valid Incident ID.")

# Logout button
st.divider()
if st.button("Log out"):
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.info("You have been logged out.")
    st.switch_page("Home.py")