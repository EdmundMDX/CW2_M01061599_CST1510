import streamlit as st
from google import genai

# Initialize GenAI client
# Ensure your Streamlit secrets are configured for GEMINI_API_KEY
# Accessing secrets like this is standard practice in Streamlit deployments
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

# Page title
st.title("🛡️ Cybersecurity AI Assistant")

# --- Initialize session state for messages ---
if 'messages' not in st.session_state:
  # Messages must be in the format the Streamlit chat UI expects (role: user/model/system)
  st.session_state.messages = [
    {
	  "role":	"system",
	  "content":	"""You	are	a	cybersecurity	expert	assistant.
	  -	Analyze	incidents	and	threats
	  -	Provide	technical	guidance
	  -	Explain	attack	vectors	and	mitigations
	  -	Use	standard	terminology	(MITRE	ATT&CK,	CVE)
	  -	Prioritize	actionable	recommendations
	  Tone:	Professional,	technical
	  Format:	Clear,	structured	responses"""
	}
  ]

# Display all previous messages
for message in st.session_state.messages:
  if	message["role"]	!=	"system":		#	Don't	display	system	prompt
    with st.chat_message(message["role"]):
      st.markdown(message["content"])

# --- Main logic for getting user input and calling the API ---

# Get user input
prompt = st.chat_input("Ask about cybersecurity...")

if prompt:
  # Display user message
  with st.chat_message("user"):
   st.markdown(prompt)

  # Add user message to session state in the Streamlit format
  st.session_state.messages.append({
    "role": "user",
    "content": prompt
  })

  # --- START OF FIXED CODE ---
  
  # 1. Extract the system instruction (the first message)
  system_instruction = st.session_state.messages[0]["content"]

  # 2. Map the Streamlit messages format to the Gemini API 'Contents' format
  gemini_contents = []
  # Iterate through history, skipping the system prompt (starting from index 1)
  for message in st.session_state.messages[1:]:
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
    st.session_state.messages.append({
      "role": "model",
      "content": response
    })

  except Exception as e:
    st.error(f"An API error occurred: {e}")
  # --- END OF FIXED CODE ---