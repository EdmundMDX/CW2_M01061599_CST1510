import streamlit as st
import sqlite3
import pandas as pd
from google import genai

# Configuration 
DB_FILE = "intelligence_platform.db"
TABLE_NAME = "cyber_incidents" 

# Database Functions
def get_db_connection():
    """Establishes and returns the SQLite database connection."""
    try:
        conn = sqlite3.connect(DB_FILE)
        return conn
    except sqlite3.Error as e:
        st.error(f"Error connecting to database: {e}")
        return None

def fetch_incident_data():
    """Fetches all incident data and returns it as a Pandas DataFrame."""
    conn = get_db_connection()
    if conn:
        try:
            # Fetch essential columns for analysis and display
            query = f"SELECT incident_id, severity, category, description, status FROM {TABLE_NAME}" 
            df = pd.read_sql_query(query, conn)
            conn.close()
            # Rename 'category' to 'incident_type' for consistent display/prompting
            df.rename(columns={'category': 'incident_type'}, inplace=True)
            return df
        except pd.io.sql.DatabaseError as e:
            st.error(f"Error fetching data: {e}. Check if table '{TABLE_NAME}' exists and columns are correct.")
            return pd.DataFrame()
    return pd.DataFrame()


# Gemini API Client Initialization 
try:
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
except KeyError:
    st.error("🚨 GEMINI_API_KEY not found in Streamlit secrets. Please configure it.")
    client = None

# --- Streamlit Application Layout 
st.set_page_config(layout="wide", page_title="Cybersecurity AI Aissistant") 
st.title("🛡️ Cybersecurity AI Aissistant")
st.markdown("---")

# Use tabs to separate the two main features
tab_analyzer, tab_assistant = st.tabs([
    "🔍 Incident Analyzer", 
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

# 1. Incident Analyzer Tab
with tab_analyzer:
    st.header("🔍 Structured Incident Response Analysis")
    st.markdown("Select an incident from the database to generate a detailed root cause, action plan, and risk assessment using Gemini 2.5 Flash.")

    data_df = fetch_incident_data()

    if data_df.empty:
        st.warning("No incidents found in the database. Analysis cannot be performed.")
        st.stop()

    # Prepare selection options
    incident_options = [
        f"{row['incident_id']}: {row['incident_type']} - {row['severity']}"
        for index, row in data_df.iterrows()
    ]

    # Incident Selection
    selected_idx = st.selectbox(
        "Select incident to analyze:",
        range(len(data_df)),
        format_func=lambda i: incident_options[i]
    )

    selected_incident = data_df.iloc[selected_idx].to_dict()

    # Display incident details
    st.subheader("📋 Selected Incident Details")
    col1, col2 = st.columns(2)
    col1.write(f"**Incident ID:** {selected_incident.get('incident_id', 'N/A')}")
    col1.write(f"**Type:** {selected_incident.get('incident_type', 'N/A')}")
    col2.write(f"**Severity:** {selected_incident.get('severity', 'N/A')}")
    col2.write(f"**Status:** {selected_incident.get('status', 'N/A')}")

    st.info(f"**Description:** {selected_incident.get('description', 'No description provided.')}")
    st.markdown("---")

    # Analysis Trigger
    if st.button("🤖 Analyze with Gemini", type="primary"):
        
        if client is None:
            st.error("AI analysis aborted due to missing API key.")
            st.stop()

        with st.spinner("Gemini 2.5 Flash is analyzing the incident..."):
            
            # Create analysis prompt
            analysis_prompt = f"""
            Perform a comprehensive analysis of the following cybersecurity incident.
            
                INCIDENT DETAILS
            Incident ID: {selected_incident.get('incident_id', 'N/A')}
            Type: {selected_incident.get('incident_type', 'N/A')}
            Severity: {selected_incident.get('severity', 'N/A')}
            Status: {selected_incident.get('status', 'N/A')}
            Description: {selected_incident.get('description', 'No description provided.')}
                END DETAILS

            Provide a highly detailed, professional response structured with the following four mandatory Markdown headings:

            ## 1. Root Cause Analysis
            Explain the most likely technical and procedural failures that led to this incident.

            ## 2. Immediate Actions Needed
            List the critical, first-response steps to contain and eradicate the threat.

            ## 3. Long-Term Prevention Measures
            Outline strategic recommendations for policy, technology, and training to prevent recurrence.

            ## 4. Risk Assessment
            Summarize the potential impact (e.g., financial, reputational, regulatory) and overall risk level.
            """

            # Define the system persona for Gemini
            system_instruction = "You are a highly experienced and certified cybersecurity expert. Your analysis must be technical, structured, and actionable. Use clear, concise Markdown formatting for all output."

            # Prepare the contents for the API call
            contents = [
                {
                    "role": "user",
                    "parts": [{"text": analysis_prompt}]
                }
            ]
            
            try:
                # Call Gemini 2.5 Flash
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=contents,
                    config={"system_instruction": system_instruction}
                )
                
                # Display AI analysis
                st.subheader("🧠 Detailed AI Analysis")
                st.markdown(response.text)
                
            except Exception as e:
                st.error(f"Error during Gemini API call. Error: {e}")

    st.divider()
    st.subheader("Raw Incident Data Table")
    st.dataframe(data_df, use_container_width=True)

# 2. AI Chat Assistant Tab
with tab_assistant:
    st.header("💬 Cybersecurity AI Chat Assistant")
    st.markdown("Ask general questions about threats, protocols, attack vectors, or mitigation strategies.")

    # Initialize session state for messages 
    if 'chat_messages' not in st.session_state:
        # Use a different key ('chat_messages') to avoid collision with other session state keys
        st.session_state.chat_messages = [
            {
                "role": "system",
                "content": """You are a highly knowledgeable and professional cybersecurity expert assistant.
                - Analyze incidents and threats.
                - Provide technical guidance.
                - Explain attack vectors and mitigations using standard terminology (MITRE ATT&CK, CVE).
                - Prioritize actionable recommendations.
                Tone: Professional, technical.
                Format: Clear, structured responses using Markdown."""
            }
        ]

    # Display all previous messages
    for message in st.session_state.chat_messages:
        # Don't display the system prompt in the chat window
        if message["role"] != "system":
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # Main logic for getting user input and calling the API 

    # Get user input
    prompt = st.chat_input("Ask about cybersecurity...", key="chat_input_key")

    if prompt:
        
        if client is None:
            st.error("Chat functionality aborted due to missing API key.")
            st.stop()

        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)

        # Add user message to session state in the Streamlit format
        st.session_state.chat_messages.append({
            "role": "user",
            "content": prompt
        })

        # 1. Extract the system instruction (the first message)
        system_instruction = st.session_state.chat_messages[0]["content"]

        # 2. Map the Streamlit messages format to the Gemini API 'Contents' format
        gemini_contents = []
        # Iterate through history, skipping the system prompt (starting from index 1)
        for message in st.session_state.chat_messages[1:]:
            # Ensure the role is what the API expects ('user' or 'model')
            role = message["role"]
            if role == "assistant":
                role = "model"

            gemini_contents.append({
                "role": role,
                "parts": [{"text": message["content"]}]
            })

        # 3. Call GenAI API with the correctly formatted contents and system instruction
        try:
            with st.spinner("Gemini is thinking..."):
                completion = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=gemini_contents, # History contains only user/model roles
                    config={"system_instruction": system_instruction} # System instruction passed separately
                )

            # Extract assistant response
            response = completion.text

            # Display assistant response
            with st.chat_message("model"):
                st.markdown(response)

            # Add assistant response back to Streamlit's session state
            st.session_state.chat_messages.append({
                "role": "model",
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