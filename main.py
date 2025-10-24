import os
import streamlit as st
from dotenv import load_dotenv

# Import the new Google Client SDK
from google import genai
from google.genai.errors import APIError

# --- CONFIGURATION CONSTANTS ---

# Define creator details as constants
CREATOR_NAME = "Ankit Nandoliya"
CREATOR_PORTFOLIO = "https://ankit52-git-main-ankitnandoliya32-8971s-projects.vercel.app/"
CREATOR_KEYWORDS = [
    "who built you", "who made you", "your creator", 
    "your developer", "who created you", "who is ankit", 
    "tell me about ankit", "who is my master", "tell me about yourself"
]

# Detailed profile for the custom response
CREATOR_PROFILE = """
**Ankit Nandoliya** is a software developer focused on full-stack development and artificial intelligence integration. He creates smooth user experiences and stable, scalable backend systems.

**Key Expertise:**
* **Full Stack Development:** Experienced with modern JavaScript frameworks (like React or Angular) and Python/Node.js for backend services.
* **AI/ML Integration:** Works with generative models and APIs to build intelligent applications, like this J.A.R.V.I.S. system.
* **Cloud & Deployment:** Familiar with setting up applications using platforms like Vercel and similar cloud services.

He approaches projects with a focus on problem-solving and attention to detail.
"""

# Use a standard, stable model name
MODEL_NAME = "gemini-2.5-flash" 


# --- API KEY & MODEL INITIALIZATION ---

# Load environment variables from .env (for local testing)
try:
    load_dotenv()
except ImportError:
    pass

# Configure API key (from environment variable or Streamlit Secrets)
# The google-genai client automatically looks for GOOGLE_API_KEY environment variable.
api_key = os.getenv("GOOGLE_API_KEY") or st.secrets.get("GOOGLE_API_KEY")

if not api_key:
    st.error("Configuration Error: GOOGLE_API_KEY not found. Please set it in your environment variables.")
    st.stop()


# Initialize the Gemini Client object
@st.cache_resource
def get_gemini_client():
    """Initializes and returns the Gemini client."""
    try:
        # The Client() automatically uses the GOOGLE_API_KEY env variable
        client = genai.Client()
        return client
    except Exception as e:
        st.error(f"Client Initialization Error: {e}")
        st.stop()

# Initialize Chat Session
@st.cache_resource
def get_chat_session(client):
    """Initializes and returns a chat session with Google Search enabled as a tool."""
    try:
        # The 'google_search' tool is enabled here for real-time data access
        chat = client.chats.create(
            model=MODEL_NAME,
            config=genai.types.GenerateContentConfig(
                tools=[{"google_search": {}}] # Standard dict format for tools
            )
        )
        return chat
    except Exception as e:
        # This error often occurs if the API key lacks necessary permissions or 
        # the network blocks the tool initialization.
        st.warning("Could not enable Google Search Tool for real-time data. Using internal model data.")
        # Fallback to chat session without tools
        chat = client.chats.create(model=MODEL_NAME)
        return chat


# --- STREAMLIT APP SETUP ---

st.set_page_config(
    page_title="J.A.R.V.I.S.",
    page_icon="💻",
    layout="centered",
)

st.title("💻 J.A.R.V.I.S. AI System")

# Get client and chat session
gemini_client = get_gemini_client()
chat_session = get_chat_session(gemini_client)

# Chat history stored in session state
if "messages" not in st.session_state:
    st.session_state.messages = []
    # INITIAL GREETING MESSAGE
    st.session_state.messages.append({
        "role": "assistant",
        "text": "Greetings, I am J.A.R.V.I.S. How may I assist you today?"
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

    ai_text = ""
    
    # 1. Custom Question Handling (Bypass API)
    is_creator_query = any(keyword in user_input.lower() for keyword in CREATOR_KEYWORDS)

    if is_creator_query:
        # Hardcoded response for creator identity
        ai_text = (
            f"I was built by the developer, **{CREATOR_NAME}**. "
            f"\n\n--- **Creator Profile and History** ---\n\n"
            f"{CREATOR_PROFILE}"
            f"\n\nFor more details on his projects and technical background, please visit his portfolio here: **[{CREATOR_PORTFOLIO}]({CREATOR_PORTFOLIO})**"
        )
    else:
        # 2. Normal Gemini API Call
        try:
            # Send the message to the chat session (which maintains history)
            response = chat_session.send_message(user_input)
            
            # The 'google-genai' SDK returns a Response object
            ai_text = response.text

        except APIError as e:
            # Fallback if API call fails
            st.error(f"I encountered an API error trying to access the AI: {e}")
            ai_text = "My systems are currently experiencing a brief technical fault."

        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")
            ai_text = "My systems are currently experiencing a brief technical fault."


    # 3. Display and Save AI response (from custom handler or API)
    if ai_text:
        with st.chat_message("assistant"):
            st.markdown(ai_text)
            
        # Save AI response in session
        st.session_state.messages.append({"role": "assistant", "text": ai_text})
