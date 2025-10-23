import os
import streamlit as st
from dotenv import load_dotenv
import google.generativeai as genai

# Define creator details as constants
CREATOR_NAME = "Ankit Nandoliya"
CREATOR_PORTFOLIO = "https://ankit52-git-main-ankitnandoliya32-8971s-projects.vercel.app/"
CREATOR_KEYWORDS = ["who built you", "who made you", "your creator", "your developer", "who created you", "who is ankit"]

# --- ADDED DETAILED PROFILE HISTORY (Simplified) ---
CREATOR_PROFILE = """
**Ankit Nandoliya** is a software developer focused on full-stack development and artificial intelligence integration. He creates smooth user experiences and stable, scalable backend systems.

**Key Expertise:**
* **Full Stack Development:** Experienced with modern JavaScript frameworks (like React or Angular) and Python/Node.js for backend services.
* **AI/ML Integration:** Works with generative models and APIs to build intelligent applications, like this J.A.R.V.I.S. system.
* **Cloud & Deployment:** Familiar with setting up applications using platforms like Vercel and similar cloud services.

He approaches projects with a focus on problem-solving and attention to detail.
"""
# --- END ADDED DETAILED PROFILE HISTORY ---

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
    page_title="J.A.R.V.I.S.",
    page_icon="💻",
    layout="centered",
)

# --- NEW FUNCTION FOR HISTORY SIDEBAR ---
def show_history_sidebar():
    """Displays user's question history in the Streamlit sidebar."""
    st.sidebar.title("💬 Conversation History")
    
    # Filter for user messages and reverse to show most recent first
    # Skips the initial greeting message if present (by looking for 'user' role)
    user_queries = [
        msg['text'] for msg in st.session_state.messages 
        if msg['role'] == 'user'
    ][::-1] 

    if user_queries:
        # Add a clear history button at the top of the sidebar history list
        if st.sidebar.button("🗑️ Clear Chat History"):
            st.session_state.messages = [{
                "role": "assistant",
                "text": "Hi I am Jarvis"
            }]
            st.experimental_rerun()
            
        st.sidebar.markdown("---")
        
        # Display each query
        st.sidebar.markdown("**Recent Questions:**")
        for i, query in enumerate(user_queries):
            # Truncate for cleaner display
            display_text = query[:45] + ('...' if len(query) > 45 else '')
            # Display as a simple markdown list item
            st.sidebar.markdown(f"**-** *{display_text}*")
            
    else:
        st.sidebar.info("Start a conversation to see your recent questions here.")
# --- END NEW FUNCTION ---

st.title("💻 J.A.R.V.I.S. AI System")

# CALL THE NEW SIDEBAR FUNCTION HERE
show_history_sidebar()

# Choose Gemini model (gemini-2.5-flash is the current stable name)
MODEL_NAME = "gemini-2.5-flash"

# Initialize the model
model = genai.GenerativeModel(MODEL_NAME)

# Chat history stored in session state
if "messages" not in st.session_state:
    st.session_state.messages = []
    # INITIAL GREETING MESSAGE
    st.session_state.messages.append({
        "role": "assistant",
        "text": "Hi I am Jarvis"
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
        # 2. Normal Gemini API Call (if not a custom question)
        try:
            # Format the entire conversation history (for memory)
            contents = []
            for msg in st.session_state.messages:
                 # The API expects role 'model' for the assistant's responses
                 role = "user" if msg["role"] == "user" else "model" 
                 
                 # Using the dictionary list structure to avoid type errors
                 contents.append(
                     {"role": role, "parts": [{"text": msg["text"]}]}
                 )
            
            # Call generate_content with history (memory)
            response = model.generate_content(contents) 
            ai_text = response.text

        except Exception as e:
            # Fallback if API call fails
            st.error(f"I encountered an error trying to access the AI: {e}")
            ai_text = "My systems are currently experiencing a brief technical fault. Please try again."

    # 3. Display and Save AI response (from custom handler or API)
    if ai_text:
        with st.chat_message("assistant"):
            st.markdown(ai_text)
            
        # Save AI response in session
        st.session_state.messages.append({"role": "assistant", "text": ai_text})
