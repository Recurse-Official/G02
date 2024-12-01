import streamlit as st
import os
from dotenv import load_dotenv
import json
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Set the page title and metadata
st.set_page_config(page_title="MindHaven", page_icon="🧠")

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
    "temperature": 0.9,  # Higher temperature for a more human-like response
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

# Initialize session state for conversation history
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []

# Load and validate existing conversation history
try:
    with open("conversation_history.json", "r") as file:
        saved_history = json.load(file)
        st.session_state.conversation_history = saved_history
except FileNotFoundError:
    pass  # Start with an empty history if no file exists

# Title and introduction
st.title("MindHaven 🧠")
st.markdown(
    "Welcome to *MindHaven*, your supportive mental health companion. "
    "Feel free to share your thoughts. I'm here to listen and provide supportive responses."
)

# Display chat messages
for message in st.session_state.conversation_history:
    if message["role"] == "user":
        st.chat_message("user", message["parts"][0]["text"])
    elif message["role"] == "model":
        st.chat_message("assistant", message["parts"][0]["text"])

# Input field for user message
if user_message := st.chat_input("How are you feeling today?"):
    # Add user message to conversation history
    st.session_state.conversation_history.append({
        "role": "user",
        "parts": [{"text": user_message}],
    })

    # Generate bot's response
    try:
        prompt = f"""
        You are a thoughtful and understanding assistant. Your responses should reflect a deep understanding of the user's emotions. Be attentive to their feelings and provide genuine, human-like responses that are insightful and supportive. Avoid starting with "I'm sorry" or standard empathetic phrases. Instead, engage with what they say directly, offer encouragement, and acknowledge their emotions in a meaningful way.

        User: {user_message}

        Response:
        """
        convo = model.start_chat(history=st.session_state.conversation_history)
        response = convo.send_message(prompt)

        # Add bot's response to conversation history
        bot_message = response.text.strip()
        st.session_state.conversation_history.append({
            "role": "model",
            "parts": [{"text": bot_message}],
        })

        # Display bot's response
        st.chat_message("assistant", bot_message)

        # Save updated conversation history
        with open("conversation_history.json", "w") as file:
            json.dump(st.session_state.conversation_history, file)

    except Exception as e:
        st.error(f"Error during response generation: {e}")
