import os
import streamlit as st
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables from .env
load_dotenv()

# Configure API key (make sure your .env file has GOOGLE_API_KEY)
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Streamlit page settings
st.set_page_config(
    page_title="Generative AI Chatbot",
    page_icon="🤖",
    layout="centered",
)

st.title("🤖 Generative AI Chatbot")

# Choose Gemini model 
# NOTE: Using gemini-2.5-flash to avoid the 404 error from the very first attempt.
MODEL_NAME = "gemini-2.5-flash"

# Initialize the model
try:
    model = genai.GenerativeModel(MODEL_NAME)
except Exception as e:
    st.error(f"Failed to initialize the Generative AI model. Error: {e}")
    st.stop()


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
        # Generate response from Gemini
        # NOTE: This simple call does not pass the full conversation history.
        response = model.generate_content(user_input)

        # Display AI response
        ai_text = response.text
        st.chat_message("assistant").markdown(ai_text)

        # Save AI response in session
        st.session_state.messages.append({"role": "assistant", "text": ai_text})

    except Exception as e:
        st.error(f"Error: {e}")
