import streamlit as st
from datetime import datetime
from firebase_admin import credentials, firestore, initialize_app
from firebase_admin import _apps
import google.generativeai as genai
from fpdf import FPDF
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Generative AI
api_key = os.getenv("GENAI_API_KEY")
if not api_key:
    api_key = st.secrets.get("GENAI_API_KEY")
    if not api_key:
        st.error("Please set the GENAI_API_KEY environment variable.")
        st.stop()

genai.configure(api_key=api_key)

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

# Firebase Initialization
if not _apps:
    cred = credentials.Certificate("firebase-key.json")
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

def generate_supportive_response(user_entry):
    try:
        prompt = f"""
        You are an empathetic AI assistant. Read the following journal entry and provide a thoughtful, kind, and encouraging comment to support the writer's emotions and reflections:
        
        Journal Entry:
        "{user_entry}"
        
        Please ensure the response is positive, uplifting, and human-like.
        """
        response = model.generate_content(prompt)
        if response and response.text:
            comment = response.text.strip().split('.')[0] + "."
            return comment
        else:
            return "That was a heartfelt entry. Keep writing and reflecting!"
    except Exception as e:
        st.warning(f"Error generating AI response: {e}")
        return "Your journaling is inspiring. Keep it up!"

# PDF Export Function
def create_pdf(entries):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    for entry in entries:
        pdf.cell(0, 10, f"Date: {entry['date']}", ln=True)
        pdf.multi_cell(0, 10, f"Entry: {entry['entry']}\n", border=0, align="L")
    return pdf.output(dest="S").encode("latin1")

# Streamlit App
st.title("MindHaven: Journaling with Supportive AI")

st.sidebar.title("Navigation")
menu = st.sidebar.radio("Go to:", ["Add Journal", "View Journals", "Settings"])

if menu == "Add Journal":
    st.subheader("Add a New Journal Entry")
    with st.form(key="journal_form"):
        journal_entry = st.text_area("Write your thoughts:", placeholder="What's on your mind?")
        submit_button = st.form_submit_button("Add Entry")

        if submit_button:
            if journal_entry.strip():
                try:
                    # Add the entry to Firestore
                    add_entry_to_firestore(journal_entry)
                    st.success("Journal entry added successfully!")

                    # Generate AI response for the current entry
                    with st.spinner("Generating a supportive comment..."):
                        supportive_response = generate_supportive_response(journal_entry)

                    # Display the AI's comment
                    st.markdown(f"**MindHaven's Comment:** *{supportive_response}*")

                except Exception as e:
                    st.error(f"Error adding entry: {e}")
            else:
                st.error("Entry cannot be empty.")

elif menu == "View Journals":
    st.subheader("Your Journal Entries")
    entries = get_entries_from_firestore()

    if entries:
        for entry in entries:
            date = entry['date'][:10]  # Extract date part (YYYY-MM-DD)
            st.markdown(f"**{date}: {entry['entry']}**")

            # Generate AI comment for each entry
            with st.spinner("Generating AI comment..."):
                supportive_response = generate_supportive_response(entry['entry'])
            st.markdown(f"**MindHaven's Comment:** *{supportive_response}*")
    else:
        st.info("No journal entries yet. Start writing!")

    # Export as PDF
    if st.button("Download All Journal Entries as PDF"):
        pdf_data = create_pdf(entries)
        st.download_button(
            label="Download Journal Entries (PDF)",
            data=pdf_data,
            file_name="journal_entries.pdf",
            mime="application/pdf"
        )

elif menu == "Settings":
    st.subheader("Settings")
    st.write("Settings functionality will go here in the future.")
