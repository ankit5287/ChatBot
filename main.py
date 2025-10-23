import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Configure API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Set page config
st.set_page_config(page_title="Gemini Chatbot 🤖", page_icon="💬")

st.title("💬 Gemini AI Chatbot")

# Create the model
model = genai.GenerativeModel("gemini-1.5-flash")

# Chat interface
user_input = st.text_input("Ask something:")

if st.button("Send"):
    if user_input.strip():
        response = model.generate_content(user_input)
        st.write("**Gemini:**", response.text)
    else:
        st.warning("Please enter a question.")

