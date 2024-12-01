import streamlit as st
import os
from dotenv import load_dotenv
import json
import requests
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Spotify API credentials
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

# Function to get Spotify API token
def get_spotify_token():
    auth_url = "https://accounts.spotify.com/api/token"
    auth_response = requests.post(
        auth_url,
        data={"grant_type": "client_credentials"},
        auth=(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET),
    )
    auth_response_data = auth_response.json()
    return auth_response_data.get("access_token")

spotify_token = get_spotify_token()

# Spotify recommendations API function
def get_song_recommendations(mood):
    endpoint = "https://api.spotify.com/v1/recommendations"
    mood_to_genre = {
        "happy": "happy",
        "sad": "sad",
        "energetic": "workout",
    }
    genre = mood_to_genre.get(mood, "pop")  # Default to "pop" if no mood matches
    params = {
        "limit": 1,  # Fetch one recommendation
        "seed_genres": genre,
    }
    headers = {"Authorization": f"Bearer {spotify_token}"}
    response = requests.get(endpoint, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        if data["tracks"]:
            track = data["tracks"][0]
            # Extract track information
            track_name = track["name"]
            artist_name = track["artists"][0]["name"]
            spotify_link = track["external_urls"]["spotify"]
            return f"[{track_name} by {artist_name}]({spotify_link})"
    return "Sorry, I couldn't find a song recommendation at the moment."

# Configure the generative AI model
genai.configure(api_key=os.getenv("GENAI_API_KEY"))
generation_config = {
    "temperature": 0.9,
    "top_p": 1,
    "top_k": 32,
    "max_output_tokens": 8192,
}
model = genai.GenerativeModel(
    model_name="gemini-pro",
    generation_config=generation_config,
)

# Function to detect mood from user input
def detect_mood(user_input):
    mood_keywords = {
        "happy": ["happy", "joy", "excited", "love"],
        "sad": ["sad", "down", "depressed", "cry"],
        "energetic": ["energetic", "motivated", "active", "power"],
    }
    for mood, keywords in mood_keywords.items():
        if any(word in user_input.lower() for word in keywords):
            return mood
    return None

# Initialize conversation history
try:
    with open("conversation_history.json", "r") as file:
        conversation_history = json.load(file)
except FileNotFoundError:
    conversation_history = []

# Start the chat session
st.title("MindHaven 🧠")
st.markdown(
    "Welcome to *MindHaven*, your supportive mental health companion. "
    "Feel free to share your thoughts. I'm here to listen, provide supportive responses, "
    "and recommend uplifting music dynamically!"
)

user_input = st.text_input("You:", placeholder="How are you feeling today?")

if st.button("Send"):
    if user_input.strip():
        mood = detect_mood(user_input)

        # Add user input to conversation history
        conversation_history.append({"role": "user", "parts": [{"text": user_input}]})

        # Generate bot response
        prompt = f"""
        You are a thoughtful and understanding assistant. Your responses should reflect a deep understanding of the user's emotions. Be attentive to their feelings and provide genuine, human-like responses that are insightful and supportive.
        User: {user_input}
        Response:
        """
        response = model.start_chat(history=conversation_history).send_message(prompt)
        bot_response = response.text.strip()

        # Add song recommendation if mood detected
        if mood:
            song_recommendation = get_song_recommendations(mood)
            bot_response += f"\n\nHere's a song recommendation to uplift your mood: {song_recommendation} 🎵"

        # Add bot response to conversation history
        conversation_history.append({"role": "model", "parts": [{"text": bot_response}]})

        # Display bot's response
        st.caption("*MindHaven's Response:*")
        st.write(bot_response)

        # Save conversation history
        with open("conversation_history.json", "w") as file:
            json.dump(conversation_history, file)
    else:
        st.warning("Please enter a message before sending.")
