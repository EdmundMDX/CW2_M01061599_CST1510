import streamlit as st
import sqlite3
import pandas as pd
from google import genai
from datetime import datetime

# --- Configuration ---
DB_FILE = "intelligence_platform.db"
TABLE_NAME = "metadata" # Target table for metadata analysis

# Database Functions
def get_db_connection():
    """Establishes and returns the SQLite database connection."""
    try:
        conn = sqlite3.connect(DB_FILE)
        return conn
    except sqlite3.Error as e:
        st.error(f"Error connecting to database: {e}")
        return None

def fetch_metadata_data(table):
    """Fetches all data from the specified table and returns it as a Pandas DataFrame."""
    conn = get_db_connection()
    if conn:
        try:
            query = f"SELECT * FROM {table}" 
            df = pd.read_sql_query(query, conn)
            
            if 'upload_date' in df.columns:
                # Convert date column to datetime objects
                df['upload_date'] = pd.to_datetime(df['upload_date'], errors='coerce') 
            
            return df
        except pd.io.sql.DatabaseError as e:
            st.error(f"Error fetching data from table '{table}': {e}. Please ensure the table exists.")
            return pd.DataFrame()
        finally:
            conn.close()
    return pd.DataFrame()


# Gemini API Client Initialization 
try:
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
except KeyError:
    st.error("🚨 GEMINI_API_KEY not found in Streamlit secrets. Please configure it.")
    client = None

# Streamlit Application Layout 
st.set_page_config(layout="wide", page_title="Metadata AI Assistant")
st.title("📊 Metadata AI Assistant")
st.markdown("---")

# Use tabs to separate the two main features
tab_analyzer, tab_assistant = st.tabs([
    "🧠 Structured Data Analyzer", 
    "💬 AI Chat Assistant"
])

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

# Structured Data Analyzer Tab
with tab_analyzer:
    st.header("🧠 Dataset Metadata Analyzer")
    st.markdown("Uses **Gemini 2.5 Flash** to find dependencies, correlations, and insights within the dataset metadata.")
    
    metadata_df = fetch_metadata_data(TABLE_NAME)

    if metadata_df.empty:
        st.warning(f"No data found in the '{TABLE_NAME}' table. Cannot perform analysis.")
        st.stop()

    # Display Metadata Overview
    st.subheader(f"📊 {TABLE_NAME.capitalize()} Overview")
    st.metric("Total Datasets (Record Count)", len(metadata_df))
    st.dataframe(metadata_df, use_container_width=True)
    st.markdown("---")
    
    if st.button("🤖 Analyze Correlations with AI", type="primary"):
        
        if client is None:
            st.error("AI analysis aborted due to missing API key.")
            st.stop()
            
        with st.spinner("Gemini 2.5 Flash is analyzing data correlation and dependencies..."):
            
            # Format DataFrame for the AI prompt
            metadata_str = metadata_df.to_csv(index=False)
            
            analysis_prompt = f"""
            You are a professional Data Analyst and Statistical Expert. Your task is to perform a detailed analysis on the provided dataset metadata.
            
            DATASET METADATA
            {metadata_str}
            END METADATA 

            Analyze the data to find meaningful correlations, dependencies, and statistical insights between the columns (e.g., 'rows', 'columns', 'uploaded_by', 'upload_date', 'name').

            Provide a highly detailed analysis structured with the following three mandatory Markdown headings:

            ## 1. Key Observations and Outliers
            Point out any datasets or metrics that stand out as significantly larger, smaller, or unusual (e.g., the largest dataset by rows or the dataset with the most columns).

            ## 2. Quantitative Correlations and Trends
            Analyze the relationship between numerical fields ('rows' vs. 'columns' vs. 'upload_date'). Is there a trend where newer datasets have more rows? Do larger datasets generally have more columns?

            ## 3. Categorical Dependencies and Insights
            Identify dependencies involving categorical data ('uploaded_by' vs. other fields). For example, which uploaders typically handle the largest datasets, the most recent datasets, or datasets related to specific names/topics?
            """

            system_instruction = "You are a professional Data Analyst. Your analysis must be structured, technical, and insightful. Use clear, concise Markdown formatting for all output."

            contents = [{"role": "user", "parts": [{"text": analysis_prompt}]}]
            
            try:
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=contents,
                    config={"system_instruction": system_instruction}
                )
                
                st.subheader("🧠 Detailed AI Data Analysis")
                st.markdown(response.text)
                
            except Exception as e:
                st.error(f"Error during Gemini API call: {e}")

# 2. General AI Chat Assistant Tab 
with tab_assistant:
    st.header("💬 General Data Science AI Assistant")
    st.markdown("Ask general questions about EDA, feature engineering, modeling, or Python code snippets.")

    # Initialize session state for messages
    if 'metadata_chat_messages' not in st.session_state:
        # Use a unique key to prevent collision with other chat assistants
        st.session_state.metadata_chat_messages = [
            {
                "role": "system",
                "content": """You are an expert Data Science and Machine Learning assistant.
                - Assist with Exploratory Data Analysis (EDA), feature engineering, and model selection.
                - Write, explain, and debug Python code snippets, especially using libraries like Pandas, NumPy, Scikit-learn, and Matplotlib.
                - Provide statistical insights and interpret model results.
                - Use clear, structured Markdown for explanations and include code blocks for all code.
                - Tone: Helpful, analytical, and professional."""
            }
        ]

    # Display all previous messages
    for message in st.session_state.metadata_chat_messages:
        # Don't display the system prompt
        if message["role"] != "system":
            # Map 'assistant' role for display consistency
            display_role = "assistant" if message["role"] == "model" else message["role"]
            with st.chat_message(display_role):
                st.markdown(message["content"])

    # --- Main logic for getting user input and calling the API ---
    prompt = st.chat_input("Ask about data analysis or machine learning...", key="metadata_chat_input_key")

    if prompt:
        
        if client is None:
            st.error("Chat functionality aborted due to missing API key.")
            st.stop()

        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)

        # Add user message to session state
        st.session_state.metadata_chat_messages.append({"role": "user", "content": prompt})

        # 1. Extract the system instruction 
        system_instruction = st.session_state.metadata_chat_messages[0]["content"]

        # 2. Map the Streamlit messages format to the Gemini API 'Contents' format
        gemini_contents = []
        for message in st.session_state.metadata_chat_messages[1:]:
            role = message["role"]
            if role == "assistant":
                role = "model" # Gemini API expects 'model' for assistant responses
            
            # Map Streamlit's stored 'model' role to the API's 'model' role
            if role == "model":
                 role = "model"

            gemini_contents.append({
                "role": role,
                "parts": [{"text": message["content"]}]
            })

        # 3. Call GenAI API
        try:
            with st.spinner("Gemini is thinking..."):
                completion = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=gemini_contents,
                    config={"system_instruction": system_instruction}
                )

            # Extract assistant response
            response = completion.text

            # Display assistant response
            with st.chat_message("assistant"): # Use 'assistant' for display
                st.markdown(response)

            # Add assistant response back to Streamlit's session state
            st.session_state.metadata_chat_messages.append({
                "role": "model", # Store as 'model' for API calls
                "content": response
            })

        except Exception as e:
            st.error(f"An API error occurred: {e}")

                       # Logout button
st.divider()
if st.button("Log out"):
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.info("You have been logged out.")
    st.switch_page("Home.py")