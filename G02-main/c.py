import streamlit as st
from datetime import datetime
from firebase_admin import credentials, firestore, initialize_app
from firebase_admin import _apps  # Import _apps for checking existing instances
import os
from dotenv import load_dotenv
import json
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Custom Styles
st.markdown("""
    <style>
            body {
            background-color: white;
            color: white  ;
        }
        .stTextArea textarea {
            background-color: #a9a9a921; /* Light grey background */
            color: white; /* White text */
            border-radius: 10px;
            padding: 10px;
            # background-color: white;
            # border-radius: 10px;
        }
        .stExpander {
            background-color: #9d55a6;
            border-radius: 8px;
        }
        .stButton button {
            background-color: #007bff;
            color: white;
            border-radius: 5px;
        }
    </style>
""", unsafe_allow_html=True)

# Firebase Initialization
if not _apps:
    # cred = credentials.Certificate("firebase-key.json")
    cred = credentials.Certificate(r"C:/Users/bussa/OneDrive/Documents/Desktop/WebDev/MindHaven/G02-main/firebase-key.json")
    initialize_app(cred)

db = firestore.client()

# Firestore Functions
def add_entry_to_firestore(entry):
    doc_ref = db.collection("journal").document()
    doc_ref.set({
        "date": datetime.now().isoformat(),
        "entry": entry
    })

def get_entries_from_firestore():
    journal_ref = db.collection("journal").order_by("date", direction=firestore.Query.DESCENDING)
    docs = journal_ref.stream()
    return [{"id": doc.id, "date": doc.to_dict()["date"], "entry": doc.to_dict()["entry"]} for doc in docs]

def delete_entry(entry_id):
    db.collection("journal").document(entry_id).delete()

def update_entry(entry_id, updated_entry):
    db.collection("journal").document(entry_id).update({"entry": updated_entry})

# Generative AI Setup
api_key = os.getenv("GENAI_API_KEY")
if not api_key:
    api_key = st.secrets.get("GENAI_API_KEY")
    if not api_key:
        st.error("Please set the GENAI_API_KEY environment variable.")
        st.stop()

genai.configure(api_key=api_key)

# Set up the generative AI model
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

# Streamlit App
st.title("MindHaven🧠")

st.sidebar.title("Navigation")
menu = st.sidebar.radio("Go to:", ["Chatbot", "Journal"])

if menu == "Chatbot":
    st.subheader("Chatbot Section")
    st.markdown("Welcome to **MindHaven**, your supportive mental health companion.")

    # User input for the chatbot
    user_input = st.text_input("You:", placeholder="How are you feeling today?")
    if st.button("Send", key="SendButton"):
        with st.spinner("Thinking..."):
            if user_input.strip():
                convo.send_message(user_input)
                st.caption("**Bot's Response:**")
                st.write(convo.last.text)
            else:
                st.warning("Please enter a message before sending.")

elif menu == "Journal":
    st.subheader("Your Journal")

    # Journal Input Section
    with st.form(key="journal_form"):
        journal_entry = st.text_area("Write your thoughts:", placeholder="Write about your day...")
        submit_button = st.form_submit_button("Add Entry")

        if submit_button:
            if journal_entry.strip():
                add_entry_to_firestore(journal_entry)
                st.success("Journal entry added successfully!")
            else:
                st.error("Entry cannot be empty.")

    # Display Past Journal Entries
    st.subheader("Past Entries")
    entries = get_entries_from_firestore()

    if entries:
        grouped_entries = {}
        for entry in entries:
            date = entry["date"][:10]  # Extract only the date part (YYYY-MM-DD)
            if date not in grouped_entries:
                grouped_entries[date] = []
            grouped_entries[date].append(entry)

        for date, entries_on_date in grouped_entries.items():
            with st.expander(f"Entries from {date}"):
                for entry in entries_on_date:
                    st.markdown(f"- {entry['entry']}")
                    col1, col2 = st.columns([1, 1])
                    with col1:
                        if st.button("Modify", key=f"modify_{entry['id']}"):
                            new_text = st.text_area("Edit your entry", value=entry["entry"])
                            if st.button("Save Changes", key=f"save_{entry['id']}"):
                                update_entry(entry["id"], new_text)
                                st.experimental_rerun()
                    with col2:
                        if st.button("Delete", key=f"delete_{entry['id']}"):
                            delete_entry(entry["id"])
                            st.experimental_rerun()
    else:
        st.info("No journal entries yet. Start writing!")

    # Export Button
    if st.button("Download All Journal Entries"):
        file_content = "\n\n".join([f"Date: {entry['date']}\nEntry: {entry['entry']}" for entry in entries])
        st.download_button(
            label="Download Journal Entries",
            data=file_content,
            file_name="journal_entries.txt",
            mime="text/plain"
        )
