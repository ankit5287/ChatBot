import os
import streamlit as st
from dotenv import load_dotenv
import google.generativeai as genai

# --- 1. AUTHENTICATION & CONSTANTS SETUP ---

# Define creator details as constants
CREATOR_NAME = "Ankit Nandoliya"
CREATOR_PORTFOLIO = "https://ankit52-git-main-ankitnandoliya32-8971s-projects.vercel.app/"
CREATOR_KEYWORDS = ["who built you", "who made you", "your creator", "your developer", "who created you", "who is ankit", "tell me about ankit", "who is my master", "tell me about yourself"]

# --- AUTH SESSION STATE INIT ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = None
if 'users' not in st.session_state:
    # Simulated user database for simplicity: {username: password}
    st.session_state.users = {"ankit": "password123"} 
    
if 'is_guest' not in st.session_state:
    st.session_state.is_guest = False


# --- AUTHENTICATION HANDLERS ---
def handle_login(user, password):
    st.session_state.is_guest = False
    if user in st.session_state.users and st.session_state.users[user] == password:
        st.session_state.logged_in = True
        st.session_state.username = user
        st.success(f"Access granted. Welcome, {user}!")
        st.experimental_rerun()
    else:
        st.error("Login failed: Invalid username or password.")

def handle_signup(user, password):
    st.session_state.is_guest = False
    if user in st.session_state.users:
        st.error("Sign up failed: Username already exists.")
    elif not user or not password:
        st.error("Sign up failed: Username and password cannot be empty.")
    else:
        st.session_state.users[user] = password
        st.success("Account created successfully! Please log in.")
        st.session_state.login_tab = "Login" # Switch to login tab

def handle_guest_login():
    st.session_state.is_guest = True
    st.session_state.logged_in = True
    st.session_state.username = "Guest"
    st.success("Welcome, Guest! Access granted.")
    st.experimental_rerun()

def handle_logout():
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.is_guest = False
    # Clear chat history upon logout to start fresh
    st.session_state.messages = [] 
    st.experimental_rerun()

def show_auth_screen():
    st.title("J.A.R.V.I.S. Access Portal")
    st.markdown("---")

    # Use tabs for a cleaner Login/Sign Up interface
    if 'login_tab' not in st.session_state:
        st.session_state.login_tab = "Login"
    
    # Define tab names explicitly
    LOGIN_TAB_NAME = "🔒 Login"
    SIGNUP_TAB_NAME = "✍️ Sign Up"
        
    login_tab, signup_tab = st.tabs([LOGIN_TAB_NAME, SIGNUP_TAB_NAME])
    
    # Determine the currently active tab label
    if st.session_state.login_tab == "Login":
        active_tab = login_tab
        active_tab_label = LOGIN_TAB_NAME
    else:
        active_tab = signup_tab
        active_tab_label = SIGNUP_TAB_NAME


    with active_tab:
        
        # FIX: Extract the subheader text from the known label string
        subheader_text = active_tab_label.replace('🔒 ', '').replace('✍️ ', '')
        st.subheader(subheader_text)
        
        with st.form(key=f'{subheader_text.replace(" ", "_").lower()}_form'):
            user = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button(f"{subheader_text} Now")

            if submitted:
                if subheader_text == "Login":
                    handle_login(user, password)
                else:
                    handle_signup(user, password)
                    # Force switch to login tab after successful signup
                    if st.session_state.get('login_tab') == "Login":
                        st.session_state.login_tab = "Login" 
                        st.experimental_rerun() # Rerun to switch tab
                        
        # Allow switching tabs by state
        if active_tab_label == LOGIN_TAB_NAME:
            st.session_state.login_tab = "Login"
        else:
            st.session_state.login_tab = "Sign Up"
            
    st.markdown("---")
    
    # --- OPTIONAL GUEST ACCESS ---
    if st.button("Continue as Guest"):
        handle_guest_login()
        
    st.info("Hint: Use username 'ankit' and password 'password123' to log in immediately.")

# --- MAIN CHAT APPLICATION ---

def show_jarvis_chat():
    
    # Configure API key
    api_key = os.getenv("GOOGLE_API_KEY") or st.secrets.get("GOOGLE_API_KEY")

    if not api_key:
        st.error("Configuration Error: GOOGLE_API_KEY not found. Please set it in your .env file or Streamlit Secrets.")
        st.stop()
        
    genai.configure(api_key=api_key)

    # Streamlit page settings (already set in global scope, but good practice)
    # st.set_page_config(page_title="J.A.R.V.I.S.", page_icon="💻", layout="centered")

    st.title("💻 J.A.R.V.I.S. AI System")

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

# --- MAIN APP EXECUTION FLOW ---
if st.session_state.logged_in:
    # Display welcome message and logout button in the sidebar
    with st.sidebar:
        st.title("User Profile")
        if st.session_state.is_guest:
            st.markdown("**(Guest Mode - History is temporary)**")
        st.markdown(f"**Logged in as:** `{st.session_state.username}`")
        st.markdown("---")
        if st.button("🔴 Logout"):
            handle_logout()
    
    show_jarvis_chat()

else:
    # Show authentication screen
    show_auth_screen()
