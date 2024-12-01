import streamlit as st
from utils.firebase_utils import initialize_firestore, add_entry_to_firestore, get_entries_from_firestore
from utils.genai_utils import generate_supportive_response
from utils.spotify_utils import fetch_spotify_songs
from utils.pdf_utils import create_pdf
from dotenv import load_dotenv
import os

st.set_page_config(
    page_title="MindHaven: Your Companion",
    page_icon="🧠",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Load environment variables
load_dotenv()

# Initialize Firestore
db = initialize_firestore()

# Sidebar and Navigation
st.title("MindHaven: Journaling and Chat Companion")
st.sidebar.title("Navigation")
menu = st.sidebar.radio("Go to:", ["Add Journal", "View Journals", "Chatbot", "Feedback"])

if menu == "Add Journal":
    st.subheader("📝 Add a New Journal Entry")
    with st.form(key="journal_form"):
        journal_entry = st.text_area("Write your thoughts:", placeholder="What's on your mind?")
        submit_button = st.form_submit_button("Add Entry")
        if submit_button:
            if journal_entry.strip():
                add_entry_to_firestore(db, journal_entry)
                st.success("Journal entry added successfully! 😊")
                with st.spinner("Generating a supportive comment..."):
                    supportive_response = generate_supportive_response(journal_entry)
                st.markdown(f"**MindHaven's Comment:** *{supportive_response}*")
            else:
                st.error("Entry cannot be empty. 🚫")

elif menu == "View Journals":
    st.subheader("📚 Your Journal Entries")
    entries = get_entries_from_firestore(db)
    if entries:
        for entry in entries:
            st.markdown(f"**📅 {entry['date'][:10]}**")
            st.write(entry['entry'])
            with st.spinner("Generating AI comment..."):
                comment = generate_supportive_response(entry["entry"])
            st.markdown(f"**💡 MindHaven's Comment:** *{comment}*")
        if st.button("📥 Download All Journal Entries as PDF"):
            pdf_data = create_pdf(entries)
            st.download_button(
                label="Download Journal Entries (PDF)",
                data=pdf_data,
                file_name="journal_entries.pdf",
                mime="application/pdf"
            )
    else:
        st.info("No journal entries yet. Start writing! ✍️")

elif menu == "Chatbot":
    st.subheader("🤖 Chat with MindHaven")
    user_input = st.text_input("You:", placeholder="How are you feeling today? 😊")
    if st.button("Send", key="SendButton"):
        if user_input.strip():
            response = generate_supportive_response(user_input)
            st.markdown(f"**🤖 Bot's Response:** {response}")
            songs = fetch_spotify_songs(user_input)
            if songs:
                st.subheader("🎵 Here are some songs for you:")
                for song in songs:
                    st.markdown(f"- [{song['name']} by {song['artist']}]({song['url']})")
        else:
            st.warning("Please enter a message. 🚫")

elif menu == "Feedback":
    st.subheader("💬 Share Your Feedback")
    st.markdown("We value your feedback! Please let us know how we can improve. 😊")
    # Feedback form and display logic
