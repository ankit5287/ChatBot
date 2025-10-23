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
st.set_page_config(
    page_title="Generative AI Chatbot",
    page_icon="🤖",
    layout="centered",
)

st.title("🤖 Generative AI Chatbot")

# Choose Gemini model (gemini-2.5-flash is the current stable name)
MODEL_NAME = "gemini-2.5-flash"

# Initialize the model
model = genai.GenerativeModel(MODEL_NAME)

# Chat history stored in session state
if "messages" not in st.session_state:
    st.session_state.messages = []

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
        # Generate response from Gemini (this call does NOT maintain context/memory across turns)
        response = model.generate_content(user_input)

        # Display AI response
        ai_text = response.text
        with st.chat_message("assistant"):
            st.markdown(ai_text)

        # Save AI response in session
        st.session_state.messages.append({"role": "assistant", "text": ai_text})

    except Exception as e:
        st.error(f"Error: {e}")
