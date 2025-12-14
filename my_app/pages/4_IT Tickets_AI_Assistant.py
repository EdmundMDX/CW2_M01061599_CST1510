import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
from google import genai
from datetime import datetime

# Configuration 
DB_FILE = "intelligence_platform.db"
TABLE_NAME = "it_tickets" 
REQUIRED_COLS = ['ticket_id', 'priority', 'status', 'created_at']

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
    """Fetches all IT ticket data and returns it as a Pandas DataFrame."""
    conn = get_db_connection()
    if conn:
        try:
            query = f"SELECT * FROM {table}" 
            df = pd.read_sql_query(query, conn)
            
            if 'created_at' in df.columns:
                df['created_at'] = pd.to_datetime(df['created_at'], errors='coerce')
                
            return df
        except pd.io.sql.DatabaseError as e:
            st.warning(f"Warning: Error fetching data from table '{table}': {e}. Please ensure the table exists.")
            return pd.DataFrame()
        finally:
            conn.close()
    return pd.DataFrame()


# Gemini API Client Initialization 
try:
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
except KeyError:
    st.error("🚨 GEMINI_API_KEY not found in Streamlit secrets. Please configure it to enable AI analysis.")
    client = None

# Streamlit Application Layout & Tabs 
st.set_page_config(layout="wide", page_title="IT Tickets AI Assistant")
st.title("🛠️ IT Tickets AI Assistant")
st.markdown("Combines data analysis and real-time chat assistance using **Gemini 2.5 Flash**.")

tab_analysis, tab_assistant = st.tabs(["📊 Data Analysis & Correlation", "💬 Infrastructure AI Chat Assistant"])

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


# Preparing data
data_df = fetch_ticket_data(TABLE_NAME)

if data_df.empty:
    st.warning(f"No data found in the '{TABLE_NAME}' table. Please add some IT tickets to the database.")
    # Stop execution if no data is present, as analysis is impossible.
    # Note: Chat Assistant can still run without data, but we stop for the combined app.
    st.stop()

# --- Global Column Check ---
missing_cols = [col for col in REQUIRED_COLS if col not in data_df.columns]
if missing_cols:
    st.error(f"❌ Data Error: The following required columns are missing from the '{TABLE_NAME}' table: **{', '.join(missing_cols)}**. Please ensure your database table structure matches the expected schema.")
    st.stop()

# Tab 1: Data Analysis & Correlation 
with tab_analysis:
    st.header("1. Ticket Volume Trend")

    # Preprocess for trend chart (Daily volume)
    data_df['created_date'] = data_df['created_at'].dt.date
    trend_df = data_df.groupby('created_date').size().reset_index(name='Ticket_Count')

    total_tickets = len(data_df)
    open_tickets = data_df[data_df['status'] == 'Open'].shape[0]

    col_total, col_open = st.columns(2)
    col_total.metric("Total Records", total_tickets)
    col_open.metric("Currently Open", open_tickets)

    st.markdown("---")

    st.subheader("Ticket Volume Trend Over Time")
    fig_trend = px.line(
        trend_df, 
        x='created_date', 
        y='Ticket_Count', 
        title='Daily Ticket Volume',
        labels={'created_date': 'Date Created', 'Ticket_Count': 'Number of Tickets'}
    )
    st.plotly_chart(fig_trend, use_container_width=True)

    st.markdown("---")

    # 2. Priority vs. Status Correlation
    st.header("2. Priority vs. Status Correlation")
    st.markdown("This chart visualizes the distribution of tickets across **statuses** for each **priority** level.")

    # Create the cross-tabulation table
    correlation_table = pd.crosstab(
        data_df['priority'], 
        data_df['status'], 
        normalize='index' 
    ).mul(100).round(1).reset_index()

    # Melt the DataFrame for Plotly 
    correlation_long_df = correlation_table.melt(
        id_vars='priority', 
        var_name='Status', 
        value_name='Percentage'
    )

    # Define a custom order for priority for better visualization
    PRIORITY_ORDER = ['Critical', 'High', 'Medium', 'Low']
    correlation_long_df['priority'] = pd.Categorical(
        correlation_long_df['priority'], 
        categories=PRIORITY_ORDER, 
        ordered=True
    )
    correlation_long_df.sort_values('priority', inplace=True)


    fig_corr = px.bar(
        correlation_long_df,
        x='Percentage',
        y='priority',
        color='Status',
        orientation='h',
        title='Percentage of Status by Ticket Priority',
        labels={'priority': 'Ticket Priority', 'Percentage': 'Percentage of Tickets (%)'},
        category_orders={"priority": PRIORITY_ORDER},
        height=400
    )
    st.plotly_chart(fig_corr, use_container_width=True)

    # Use markdown for the table label to avoid the TypeError on older Streamlit versions
    st.markdown("**Raw Percentage Data (Status % per Priority)**")
    st.dataframe(
        correlation_table.set_index('priority'),
        use_container_width=True
    )

    st.markdown("---")

    # 3. AI Expert Correlation Analysis
    st.header("3. AI Expert Correlation Analysis")
    st.markdown("Click below to receive a strategic analysis of the Priority vs. Status correlation from the AI expert.")

    if st.button("🤖 Get AI Correlation Insights", type="primary"):
        
        if client is None:
            st.error("AI analysis aborted due to missing API key.")
            st.stop()

        with st.spinner("Gemini 2.5 Flash is analyzing the correlation data..."):
            
            correlation_str = correlation_table.to_csv(index=False)
            
            analysis_prompt = f"""
            You are a seasoned IT Operations Expert and Service Desk Manager. Analyze the following data which represents the correlation between the **Priority** and **Status** of IT support tickets. The values are the percentage of tickets in each status, grouped by priority level.

                START DATA
            {correlation_str}
                END DATA 

            Provide a professional and actionable assessment structured with the following three mandatory Markdown headings:

            ## 1. Key Operational Insights
            Identify the most significant trends and anomalies. For example: Do 'Critical' tickets have a high percentage in 'Resolved' or 'Closed'? Do 'Low' priority tickets often stay in 'Open' or 'In Progress'?

            ## 2. Bottleneck Identification
            Based on the data, identify the most likely operational bottleneck. This could be slow resolution of a specific priority level (e.g., High priority tickets stalling in 'In Progress') or disproportionate backlog in the 'Open' status.

            ## 3. Actionable Recommendations
            Provide specific, strategic recommendations to the IT Operations team to improve flow efficiency and ensure high-priority tickets are handled appropriately. Focus on prioritization strategies, resource allocation, and process improvements.
            """

            system_instruction = "You are a seasoned IT Operations Expert. Your analysis must be structured, strategic, and focused on improving IT service management (ITSM) processes. Use clear, professional, and structured Markdown."
            contents = [{"role": "user", "parts": [{"text": analysis_prompt}]}]
            
            try:
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=contents,
                    config={"system_instruction": system_instruction}
                )
                
                st.subheader("🧠 AI Expert Correlation Analysis")
                st.markdown(response.text)
                
            except Exception as e:
                st.error(f"Error during Gemini API call: {e}")

# Tab 2: Infrastructure Chat Assistant
with tab_assistant:
    st.header("💬 Infrastructure Chat Assistant")
    st.markdown("Ask the AI expert for troubleshooting, infrastructure guidance, or ITIL advice.")
    
    # Initialize session state for chat messages 
    if 'it_chat_messages' not in st.session_state:
        # The first message is the system-level instruction that sets the model's persona
        st.session_state.it_chat_messages = [
            {
                "role": "system",
                "content": """You are an expert IT Operations and Infrastructure assistant.
                - Your primary goal is to provide **practical, actionable solutions** for IT-related issues.
                - Assist with **troubleshooting** network, server, and application issues, including error message analysis.
                - Provide guidance on system **optimization**, performance tuning, and capacity planning.
                - Offer advice on ticket **management and prioritization** (e.g., using ITIL principles).
                - Help with **infrastructure guidance** for cloud platforms (AWS, Azure, GCP), virtualization, and containerization (Docker, Kubernetes).
                - Tone: Professional, technical, and solution-oriented.
                - Format: Use clear, structured Markdown for explanations and include code blocks for command-line examples or scripts."""
            }
        ]
    
    # Display all previous messages
    for message in st.session_state.it_chat_messages:
        if message["role"] != "system":
            # The original code uses 'assistant', which Streamlit maps to 'model' icon.
            display_role = "assistant" if message["role"] == "assistant" else message["role"]
            with st.chat_message(display_role):
                st.markdown(message["content"])

    # Handle user input
    if prompt := st.chat_input("Ask about a server error, network issue, or ITIL process..."):
        if client is None:
            st.error("Cannot use AI Assistant: Gemini client not initialized.")
            st.stop()
            
        # 1. Add user message to state and display
        st.session_state.it_chat_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # 2. Extract the system instruction (the first message)
        system_instruction = st.session_state.it_chat_messages[0]["content"]

        # 3. Map the Streamlit messages format to the Gemini API 'Contents' format
        gemini_contents = []
        # Iterate through history, skipping the system prompt (starting from index 1)
        for message in st.session_state.it_chat_messages[1:]:
            # Ensure the role is what the API expects ('user' or 'model')
            role = message["role"]
            # The original chat code used 'assistant' for the model response, which needs to be 'model' for the API
            if role == "assistant":
                role = "model"

            gemini_contents.append({
                "role": role,
                "parts": [{"text": message["content"]}]
            })

        # 4. Call GenAI API
        try:
            with st.spinner("AI Assistant is thinking..."):
                completion = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=gemini_contents, 
                    config={"system_instruction": system_instruction}
                )

                response = completion.text

            # 5. Display assistant response
            with st.chat_message("assistant"):
                st.markdown(response)

            # 6. Add assistant response back to Streamlit's session state
            st.session_state.it_chat_messages.append({
                "role": "assistant", # Use 'assistant' to match the display logic
                "content": response
            })
        
        except Exception as e:
            st.error(f"An error occurred during API call: {e}. Please try again.")

            # Logout button
st.divider()
if st.button("Log out"):
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.info("You have been logged out.")
    st.switch_page("Home.py")