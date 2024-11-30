import streamlit as st
import os
from dotenv import load_dotenv
import json
import google.generativeai as genai



# Check for navigation
query_params = st.experimental_get_query_params()
if query_params.get("page") == ["journal"]:
    st.experimental_set_page_config(page_title="Journal", page_icon="📓")
elif query_params.get("page") == ["chatbot"]:
    st.experimental_set_page_config(page_title="Chatbot", page_icon="🤖")

# Load environment variables
load_dotenv()

# Set the page title and metadata
#st.set_page_config(page_title="MindHaven", page_icon="🧠")

# Load the API key for the generative AI model
api_key = os.getenv("GENAI_API_KEY")
if not api_key:
    api_key = st.secrets.get("GENAI_API_KEY")
    if not api_key:
        st.error("Please set the GENAI_API_KEY environment variable.")
        st.stop()

# Configure the generative AI model
genai.configure(api_key=api_key)

# Set up the model configuration
generation_config = {
    "temperature": 0.9,
    "top_p": 1,
    "top_k": 32,
    "max_output_tokens": 8192,
}

safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
]

model = genai.GenerativeModel(
    model_name="gemini-pro",
    generation_config=generation_config,
    safety_settings=safety_settings,
)

# Load conversation history
try:
    with open("conversation_history.json", "r") as file:
        conversation_history = json.load(file)
except FileNotFoundError:
    conversation_history = []

# Start the chat with the initial conversation history
convo = model.start_chat(history=conversation_history)

# Title and introduction
st.title("MindHaven 🧠")
st.markdown("Welcome to **MindHaven**, your supportive mental health companion. Feel free to share your thoughts.")

# Sidebar for Settings
st.sidebar.title("Settings")
if st.sidebar.button("Reset Chat"):
    conversation_history.clear()
    convo = model.start_chat(history=[])
    st.sidebar.success("Chat reset successfully.")

# Pre-defined Prompts
st.sidebar.subheader("Quick Prompts")
prompt = st.sidebar.selectbox("Choose a quick prompt", ["", "Tell me a motivational quote", "How can I handle stress?"])
if prompt:
    convo.send_message(prompt)
    st.write(f"**Bot:** {convo.last.text}")

# User input
user_input = st.text_input("You:", placeholder="How are you feeling today?")

# Chatbot interaction
if st.button("Send", key="SendButton"):
    with st.spinner("Thinking..."):
        if user_input.strip():
            convo.send_message(user_input)
            st.caption("**Bot's Response:**")
            st.write(convo.last.text)
        else:
            st.warning("Please enter a message before sending.")
