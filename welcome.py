import streamlit as st
from journal_rev import display_journal
from chatbot import display_chatbot
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables and set up the model
load_dotenv()
api_key = os.getenv("GENAI_API_KEY")
if not api_key:
    st.error("GENAI_API_KEY not found. Please configure it in the environment.")
    st.stop()

genai.configure(api_key=api_key)
model = genai.GenerativeModel(
    model_name="gemini-pro",
    generation_config={
        "temperature": 0.9,
        "top_p": 1,
        "top_k": 32,
        "max_output_tokens": 8192,
    },
    safety_settings=[
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    ],
)

# Set the page title and layout
st.set_page_config(page_title="MindHaven", page_icon="🧠", layout="centered")

# Initialize session state for navigation
if "current_page" not in st.session_state:
    st.session_state.current_page = "welcome"

# Custom CSS for styling
st.markdown("""
    <style>
        body {
            background: linear-gradient(to right, #e6f7ff, #f2ffe6);
            font-family: 'Arial', sans-serif;
        }
        .welcome-container {
            text-align: center;
            margin-top: 20vh;
        }
        .stButton button {
            background-color: #007bff;
            color: white;
            padding: 10px 20px;
            border-radius: 10px;
        }
        .stButton button:hover {
            background-color: #0056b3;
        }
    </style>
""", unsafe_allow_html=True)

# Navigation logic using session state
def navigate_to(page):
    st.session_state.current_page = page

# Render pages based on the current state
if st.session_state.current_page == "welcome":
    st.markdown("<div class='welcome-container'>", unsafe_allow_html=True)
    st.markdown("<h1>Welcome to MindHaven 🧠</h1>", unsafe_allow_html=True)
    st.markdown("<p>Your supportive mental health companion.</p>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Go to Journal"):
            navigate_to("journal")
    with col2:
        if st.button("Go to Chatbot"):
            navigate_to("chatbot")

elif st.session_state.current_page == "journal":
    display_journal()

elif st.session_state.current_page == "chatbot":
    display_chatbot(model)
