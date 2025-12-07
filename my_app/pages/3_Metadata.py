import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
from datetime import datetime

# --- Configuration ---
DB_FILE = "intelligence_platform.db" # Using the same database file
TABLE_NAME = "metadata"

# Define options for the input form
UPLOAD_USERS = ['data_scientist', 'cyber_admin', 'it_admin']


# --- Database Functions ---

def get_db_connection():
    """Establishes and returns the SQLite database connection."""
    try:
        conn = sqlite3.connect(DB_FILE)
        return conn
    except sqlite3.Error as e:
        st.error(f"Error connecting to database: {e}")
        return None

def fetch_metadata_data(table):
    """Fetches all data and returns it as a Pandas DataFrame."""
    conn = get_db_connection()
    if conn:
        try:
            query = f"SELECT * FROM {table}"
            df = pd.read_sql_query(query, conn)
            # Ensure the upload_date column is ready for charting/display
            if 'upload_date' in df.columns:
                df['upload_date'] = pd.to_datetime(df['upload_date'], errors='coerce')
                
                # Note: The underlying column 'upload_date' is still datetime/date type for charts/filtering
                # This makes a string column for display in the dataframe.
                df['Display_Date'] = df['upload_date'].dt.strftime('%d/%m/%y')
                
            return df
        except pd.io.sql.DatabaseError as e:
            st.error(f"Error fetching data: {e}")
            return pd.DataFrame()
    return pd.DataFrame()

def add_new_dataset(dataset_id, name, rows, columns, uploaded_by, upload_date):
    """Inserts a new metadata record into the database."""
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            # The table must exist with these columns for this to work.
            insert_query = f"""
            INSERT INTO {TABLE_NAME} (dataset_id, name, rows, columns, uploaded_by, upload_date)
            VALUES (?, ?, ?, ?, ?, ?)
            """
            cursor.execute(insert_query, (dataset_id, name, rows, columns, uploaded_by, upload_date))
            conn.commit()
            st.success("✅ New Dataset Metadata Recorded Successfully! **Please refresh the page to update the dashboard.**")
        except sqlite3.IntegrityError as e:
            st.error(f"❌ Error: Dataset ID **{dataset_id}** may already exist. {e}")
        except sqlite3.Error as e:
            st.error(f"❌ Error adding dataset: {e}")

# A simple update function, for example, to update the dataset name.
def update_dataset_name(dataset_id, new_name):
    """Updates the name of an existing dataset record."""
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            update_query = f"""
            UPDATE {TABLE_NAME} SET name = ? WHERE dataset_id = ?
            """
            cursor.execute(update_query, (new_name, dataset_id))
            conn.commit()

            if cursor.rowcount > 0:
                st.success(f"✏️ Name for Dataset **{dataset_id}** updated to **{new_name}**. **Please refresh the page to update the dashboard.**")
            else:
                st.warning(f"⚠️ Dataset ID **{dataset_id}** not found. Name was not updated.")

        except sqlite3.Error as e:
            st.error(f"❌ Error updating dataset name: {e}")

def delete_dataset(dataset_id):
    """Deletes a dataset record based on the dataset_id."""
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            delete_query = f"""
            DELETE FROM {TABLE_NAME} WHERE dataset_id = ?
            """
            cursor.execute(delete_query, (dataset_id,))
            conn.commit()

            # Check how many rows were affected
            if cursor.rowcount > 0:
                st.success(f"🗑️ Dataset **{dataset_id}** successfully deleted. **Please refresh the page to update the dashboard.**")
            else:
                st.warning(f"⚠️ Dataset ID **{dataset_id}** not found in the database.")

        except sqlite3.Error as e:
            st.error(f"❌ Error deleting dataset: {e}")


# --- Streamlit Layout ---

st.set_page_config(layout="wide", page_title="Simple Metadata Dashboard")
st.title("🗄️ Dataset Metadata Dashboard")

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


# Created main tabs for the interface
tab_dashboard, tab_add_dataset, tab_update_metadata, tab_delete_dataset = st.tabs([
    "📊 Dashboard",
    "➕ New Dataset",
    "✏️ Update Name",
    "🗑️ Delete Dataset"
])

# Dashboard Overview
with tab_dashboard:
    st.header("Metadata Summary")

    data_df = fetch_metadata_data(TABLE_NAME)

    if not data_df.empty:

        # Key Metrics (KPIs) 
        total = len(data_df)
        total_rows = data_df['rows'].sum() if 'rows' in data_df.columns else 0

        # Calculate datasets uploaded today
        today = datetime.now().date()
        if 'upload_date' in data_df.columns:
            # Filter for dates that match today's date
            uploaded_today = data_df[data_df['upload_date'].dt.date == today].shape[0]
        else:
            uploaded_today = 0


        col_total, col_rows, col_today = st.columns(3)
        col_total.metric("Total Datasets", total)
        col_rows.metric("Total Rows Tracked", f"{total_rows:,}") # Format with comma for large numbers
        col_today.metric("Uploaded Today", uploaded_today)

        st.markdown("---")

        # Charts 
        col_chart_1, col_chart_2 = st.columns(2)

        # Chart 1: Uploaded By Distribution
        with col_chart_1:
            if 'uploaded_by' in data_df.columns:
                st.subheader("Uploader Distribution")
                uploader_counts = data_df['uploaded_by'].value_counts().reset_index()
                uploader_counts.columns = ['Uploader', 'Count']
                fig_uploader = px.bar(uploader_counts, x='Uploader', y='Count', title='Count by Uploader')
                st.plotly_chart(fig_uploader, use_container_width=True)

        # Chart 2: Dataset Size by Name 
        with col_chart_2:
            if 'columns' in data_df.columns and 'name' in data_df.columns:
                st.subheader("Column Count by Dataset Name")
                # Create a bar chart showing the number of columns for each dataset name
                fig_cols_by_name = px.bar(
                    data_df.sort_values(by='columns', ascending=False), # Sort for better visual comparison
                    x='name',
                    y='columns',
                    color='columns', # Color intensity based on column count
                    title='Column Count for Each Dataset',
                    labels={'name': 'Dataset Name', 'columns': 'Number of Columns'}
                )
                fig_cols_by_name.update_layout(xaxis_tickangle=-45) # Rotate x-axis labels for readability
                st.plotly_chart(fig_cols_by_name, use_container_width=True)
            elif data_df.empty:
                st.subheader("Column Count by Dataset Name")
                st.info("Add data to view this chart.")

        st.markdown("---")

        # --- Raw Data Table ---
        st.subheader("Raw Data")
        
        # Select and rename columns for display
        display_cols = ['dataset_id', 'name', 'rows', 'columns', 'uploaded_by', 'Display_Date']
        
        # Create a dictionary to rename the 'Display_Date' column to 'upload_date' for the UI
        rename_map = {'Display_Date': 'upload_date'}
        
        # Select the columns, sort, and rename 'Display_Date' back to 'upload_date' for user view
        data_to_display = data_df[display_cols].sort_values(by='dataset_id', ascending=True).rename(columns=rename_map)
        
        st.dataframe(data_to_display, use_container_width=True)

    else:
        st.warning(f"No data available in the '{TABLE_NAME}' table. Use the 'New Dataset' tab to add records.")

# Add New Dataset
with tab_add_dataset:
    st.header("Add New Dataset Metadata")

    with st.form("metadata_form"):

        col_id, col_name = st.columns(2)
        dataset_id = col_id.text_input("1. Dataset ID (e.g., 10)", placeholder="1")
        name = col_name.text_input("2. Dataset Name", placeholder="Customer_List_New")

        col_rows, col_cols = st.columns(2)
        rows_str = col_rows.text_input("3. Number of Rows", placeholder="15000")
        columns_str = col_cols.text_input("4. Number of Columns", placeholder="12")

        col_uploader, col_date = st.columns(2)
        uploaded_by = col_uploader.selectbox("5. Uploaded By", UPLOAD_USERS)

        # Date/Time handling: Use a datetime input for better date control
        now = datetime.now()
        upload_date_dt = col_date.date_input("6. Upload Date", now.date())
        # Combine date and time for the database string (still yyyy-mm-dd for SQLite)
        upload_date_full = f"{upload_date_dt}"

        submitted = st.form_submit_button("Submit Metadata")

        if submitted:
            # Input validation and type conversion
            if dataset_id.strip() and name.strip():
                try:
                    # Convert row/column inputs to integers
                    rows_int = int(rows_str)
                    columns_int = int(columns_str)

                    add_new_dataset(
                        dataset_id.strip(),
                        name.strip(),
                        rows_int,
                        columns_int,
                        uploaded_by,
                        upload_date_full
                    )
                except ValueError:
                    st.error("Rows and Columns must be valid numbers.")

            else:
                st.error("Dataset ID and Name are required fields.")

# Update Dataset Name
with tab_update_metadata:
    st.header("Update Dataset Name")
    st.info("💡 You can find the **Dataset ID** in the **Dashboard** tab's **Raw Data** table.")

    with st.form("update_name_form"):

        update_id = st.text_input("1. Enter Dataset ID to Update", placeholder="e.g., 1")
        new_name = st.text_input("2. Enter New Dataset Name", placeholder="e.g., Customer_List_Updated")

        update_submitted = st.form_submit_button("Update Name", type="primary")

        if update_submitted:
            if update_id.strip() and new_name.strip():
                update_dataset_name(update_id.strip(), new_name.strip())
            else:
                st.error("Please enter a valid Dataset ID and New Name.")

# Delete a Dataset
with tab_delete_dataset:
    st.header("Delete Dataset Record")
    st.warning("🚨 **Warning:** This action is permanent and cannot be undone.")

    with st.form("delete_form"):
        # Text input to get the ID to delete
        delete_id = st.text_input("Enter Dataset ID to Delete", placeholder="e.g., 0")

        # Submission button for the delete operation
        delete_submitted = st.form_submit_button("Delete Record", type="primary")

        if delete_submitted:
            if delete_id.strip():
                delete_dataset(delete_id.strip())
            else:
                st.error("Please enter a valid Dataset ID.")

# Logout button
st.divider()
if st.button("Log out"):
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.info("You have been logged out.")
    st.switch_page("Home.py")