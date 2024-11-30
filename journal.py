import streamlit as st
from datetime import datetime
from firebase_admin import credentials, firestore, initialize_app
from firebase_admin import _apps  # Import _apps for checking existing instances
from streamlit_option_menu import option_menu
import calendar
import pandas as pd
import io
from fpdf import FPDF

# Custom Styles
st.markdown("""
    <style>
        .stTextArea textarea {
            background-color: #f0f0f0;
            border-radius: 10px;
        }
        .stExpander {
            background-color: #e6f7ff;
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

def delete_entry(entry_id):
    db.collection("journal").document(entry_id).delete()

def update_entry(entry_id, updated_entry):
    db.collection("journal").document(entry_id).update({"entry": updated_entry})

# Helper Functions
def group_entries_by_date(entries):
    grouped_entries = {}
    for entry in entries:
        date = entry["date"][:10]  # Extract only the date part (YYYY-MM-DD)
        if date not in grouped_entries:
            grouped_entries[date] = []
        grouped_entries[date].append(entry)
    return grouped_entries

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
st.title("MindHaven's Journal")

st.sidebar.title("Navigation")
menu = st.sidebar.radio("Go to:", ["Chatbot", "Journal", "Settings"])

if menu == "Journal":
    st.subheader("Your Journal")

    # Journal Input Section
    with st.form(key="journal_form"):
        journal_entry = st.text_area("Write your thoughts:", placeholder="Write about your day...")
        submit_button = st.form_submit_button("Add Entry")

        if submit_button:
            if journal_entry.strip():
                try:
                    add_entry_to_firestore(journal_entry)
                    st.success("Journal entry added successfully!")
                except Exception as e:
                    st.error(f"Error adding entry: {e}")
            else:
                st.error("Entry cannot be empty.")

    # Display Past Journal Entries
    st.subheader("Past Entries")
    entries = get_entries_from_firestore()

    if entries:
        grouped_entries = group_entries_by_date(entries)
        for date, entries_on_date in grouped_entries.items():
            with st.expander(f"Entries from {date}"):
                for entry in entries_on_date:
                    st.markdown(f"- {entry['entry']}")
                    col1, col2 = st.columns([1, 1])
                    with col1:
                        if st.button("✏️ Modify", key=f"modify_{entry['id']}"):
                            new_text = st.text_area("Edit your entry", value=entry["entry"])
                            if st.button("Save Changes", key=f"save_{entry['id']}"):
                                update_entry(entry["id"], new_text)
                                st.experimental_rerun()
                    with col2:
                        if st.button("❌ Delete", key=f"delete_{entry['id']}"):
                            delete_entry(entry["id"])
                            st.experimental_rerun()
    else:
        st.info("No journal entries yet. Start writing!")

    # Export Options
    if st.button("Download All Journal Entries as PDF"):
        pdf_data = create_pdf(entries)
        st.download_button(
            label="Download Journal Entries (PDF)",
            data=pdf_data,
            file_name="journal_entries.pdf",
            mime="application/pdf"
        )

---
