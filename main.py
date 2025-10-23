import os
import streamlit as st
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables from .env
try:
    load_dotenv()
except ImportError:
    pass

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

st.title("🤖 Generative AI Chatbot (with Memory and Search)")

# Choose Gemini model
MODEL_NAME = "gemini-2.5-flash"
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
    # 1. Display and save user message to history
    st.chat_message("user").markdown(user_input)
    st.session_state.messages.append({"role": "user", "text": user_input})

    try:
        # 2. Format the entire conversation history for the API (for memory)
        contents = []
        for msg in st.session_state.messages:
             # Map Streamlit role 'assistant' to API role 'model'
             role = "user" if msg["role"] == "user" else "model" 
             contents.append(genai.types.Content(
                 role=role,
                 parts=[genai.types.Part.from_text(msg["text"])]
             ))

        # 3. Generate response with full history (memory) AND Google Search (real-time data)
        response = model.generate_content(
            contents,
            tools=[{"google_search": {}}] # <--- This enables Grounding/Search
        )

        # 4. Display AI response
        ai_text = response.text
        with st.chat_message("assistant"):
            st.markdown(ai_text)

        # 5. Save AI response in session
        st.session_state.messages.append({"role": "assistant", "text": ai_text})

    except Exception as e:
        st.error(f"Error: {e}")


