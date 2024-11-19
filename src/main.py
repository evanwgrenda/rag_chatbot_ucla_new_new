import streamlit as st
from openai import OpenAI
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from template import PROMPT_TEMPLATE

# Google Sheets setup
def setup_google_sheets():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope) # type: ignore
    client = gspread.authorize(creds) # type: ignore
    sheet = client.open("UCLAChatlogs").sheet1  # Replace "UCLAChatlogs" with your sheet name
    return sheet

sheet = setup_google_sheets()

# Get OpenAI API key from Streamlit secrets
api_key = st.secrets["OPENAI_API_KEY"]

# Instantiate OpenAI client
client = OpenAI(api_key=api_key)

# Configure Streamlit page
st.set_page_config(
    page_title="UCLA Post-Op Care Assistant",
    page_icon="🏥",
    layout="wide"
)

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Log interactions to Google Sheets
def log_to_google_sheets(user_input, assistant_response):
    timestamp = str(datetime.now())
    sheet.append_row([timestamp, user_input, assistant_response])

# Get chatbot response
def get_chatbot_response(user_input):
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": PROMPT_TEMPLATE},
                {"role": "user", "content": user_input}
            ],
            temperature=0.7,
            max_tokens=500
        )
        assistant_response = response.choices[0].message.content
        # Log to Google Sheets
        log_to_google_sheets(user_input, assistant_response)
        return assistant_response
    except Exception as e:
        return f"Error: {str(e)}"

# Streamlit UI
st.title("🏥 UCLA Post-Op Care Assistant")

# Sidebar with information
with st.sidebar:
    st.header("Important Information")
    st.warning("For Emergencies Call 911")
    st.info("""
    **Urgent Issues (Off hours/weekends)**
    Call: (310) 206-6766
    Ask for: Plastic Surgery Resident

    **Weekday Issues (8AM-5PM)**
    Call: (310) 794-7616
    Email: estayton@mednet.ucla.edu
    """)

# Main chat interface
user_input = st.chat_input("Type your question here...")

if user_input:
    with st.spinner('Getting response...'):
        # Add user input to session state
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Get assistant response
        assistant_response = get_chatbot_response(user_input)
        st.session_state.messages.append({"role": "assistant", "content": assistant_response})

# Display chat history
for message in st.session_state.messages:
    role = message["role"]
    content = message["content"]
    st.chat_message(role).write(content)

# Footer
st.markdown("---")
st.markdown("*This is an AI assistant. For medical emergencies, please call 911 or contact the clinic directly.*")
