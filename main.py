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
        # --- FIX: Start of Memory and Streaming Implementation ---
        
        # 1. Format the entire conversation history (including the current turn) for the API
        contents = []
        for msg in st.session_state.messages:
             # The API expects role 'model' for the assistant's responses
             role = "user" if msg["role"] == "user" else "model" 
             
             # Using the dictionary list structure to avoid type errors
             contents.append(
                 {"role": role, "parts": [{"text": msg["text"]}]}
             )
        
        # 2. FIX: Initialize a chat session with the full history
        # This is the most stable way to handle stateful history and streaming.
        # We exclude the final user message from the history passed here, as it will be 
        # sent separately using send_message_stream.
        history_for_chat = contents[:-1]
        
        # Start the chat session with prior history
        chat = model.start_chat(history=history_for_chat)

        # 3. FIX: Generate response using the reliable send_message_stream method
        response_stream = chat.send_message_stream(user_input)

        # --- FIX: End of Memory and Streaming Implementation ---
        
        # Display AI response using streaming logic
        ai_text = ""
        with st.chat_message("assistant"):
            # Use a placeholder to continuously update the text output
            placeholder = st.empty()
            
            for chunk in response_stream:
                if chunk.text:
                    ai_text += chunk.text
                    # Update the placeholder with the new text and a temporary cursor
                    placeholder.markdown(ai_text + "▌") 

            # Final update without the cursor
            placeholder.markdown(ai_text)
            
        # The chat object automatically handles saving history internally, 
        # but we must still update st.session_state for Streamlit's display and next turn's history setup.
        st.session_state.messages.append({"role": "assistant", "text": ai_text})

    except Exception as e:
        st.error(f"Error: {e}")
