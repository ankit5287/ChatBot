import os
import streamlit as st
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables from .env
try:
    load_dotenv()
except ImportError:
    pass # Ignore if python-dotenv is not installed in deployment

# Configure API key
api_key = os.getenv("GOOGLE_API_KEY") or st.secrets.get("GOOGLE_API_KEY")

if not api_key:
    st.error("Configuration Error: GOOGLE_API_KEY not found. Please set it in your .env file or Streamlit Secrets.")
    st.stop()
    
genai.configure(api_key=api_key)


# Streamlit page settings
# CHANGE: Set layout to wide for better use of screen space
st.set_page_config(
    page_title="J.A.R.V.I.S.", # RENAME PAGE TITLE
    page_icon="💻", # CHANGED ICON TO A MORE SUITABLE ONE
    layout="wide",
)

# --- START UI CUSTOMIZATION ---
custom_css = """
<style>
/* 1. Primary Container Styling */
.stApp {
    background-color: #f0f2f6; /* Light gray background */
}

/* 2. Main Content Block Styling (making it look like a floating card) */
.main .block-container {
    padding-top: 2rem;
    padding-right: 1rem;
    padding-left: 1rem;
    padding-bottom: 2rem;
    max-width: 1200px; /* Max width for wide layout */
    background-color: white;
    border-radius: 12px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08); /* Subtle shadow */
    margin: 0 auto;
}

/* 3. Title Styling */
h1 {
    color: #1f77b4; /* Streamlit blue color for title */
    border-bottom: 2px solid #1f77b4;
    padding-bottom: 10px;
    margin-bottom: 20px;
}

/* 4. Chat Input Styling */
.stTextInput > div > div > input {
    border-radius: 8px;
    border: 1px solid #ccc;
    padding: 10px;
}

/* 5. Chat Bubble Styling (optional, often better to leave default for simplicity) */
/* This is harder to control with the current Streamlit API, sticking to simple changes */

</style>
"""
# Inject the custom CSS
st.markdown(custom_css, unsafe_allow_html=True)
# --- END UI CUSTOMIZATION ---


st.title("💻 J.A.R.V.I.S. AI System") # RENAME MAIN TITLE

# Choose Gemini model (gemini-2.5-flash is the current stable name)
MODEL_NAME = "gemini-2.5-flash"

# Initialize the model
model = genai.GenerativeModel(MODEL_NAME)

# Chat history stored in session state
if "messages" not in st.session_state:
    st.session_state.messages = []
    # ADDED INITIAL GREETING MESSAGE HERE (REMOVED PERIOD)
    st.session_state.messages.append({
        "role": "assistant",
        "text": "Hi, I am Jarvis"
    })

# Display past messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["text"])

# Chat input
user_input = st.chat_input("Type your message...")

if user_input:
    # Display user message
    st.chat_message("user").markdown(user_input)
    st.session_state.messages.append({"role": "user", "text": user_input})

    try:
        # --- FIX: Start of Memory Implementation (Reverting to reliable non-streaming method) ---
        
        # 1. Format the entire conversation history (including the current turn) for the API
        contents = []
        for msg in st.session_state.messages:
             # The API expects role 'model' for the assistant's responses
             role = "user" if msg["role"] == "user" else "model" 
             
             # Using the dictionary list structure to avoid type errors
             contents.append(
                 {"role": role, "parts": [{"text": msg["text"]}]}
             )
        
        # 2. Revert to the stable, non-streaming call that works for memory
        response = model.generate_content(contents) 

        # --- FIX: End of Memory Implementation ---
        
        # Display AI response
        ai_text = response.text
        with st.chat_message("assistant"):
            st.markdown(ai_text)
            
        # Save AI response in session
        st.session_state.messages.append({"role": "assistant", "text": ai_text})

    except Exception as e:
        st.error(f"Error: {e}")
