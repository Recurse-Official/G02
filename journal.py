'''import streamlit as st
from datetime import datetime
from firebase_admin import credentials, firestore, initialize_app
from firebase_admin import _apps  # Import _apps for checking existing instances
from fpdf import FPDF
import google.generativeai as genai  # Gemini AI for optimistic messages

# Firebase Initialization
if not _apps:
    cred = credentials.Certificate("firebase-key.json")  # Replace with your Firebase key path
    initialize_app(cred)

db = firestore.client()

# Gemini AI Configuration
api_key = "YOUR_GENAI_API_KEY"  # Replace with your Gemini API key
genai.configure(api_key=api_key)

# Firestore Functions
def add_entry_to_firestore(entry, optimistic_message):
    db.collection("journal").add({
        "date": datetime.now().isoformat(),
        "entry": entry,
        "optimistic_message": optimistic_message
    })


def get_entries_from_firestore():
    journal_ref = db.collection("journal").order_by("date", direction=firestore.Query.DESCENDING)
    docs = journal_ref.stream()
    return [
        {"id": doc.id, "date": doc.to_dict()["date"], "entry": doc.to_dict()["entry"], "optimistic_message": doc.to_dict().get("optimistic_message", "")}
        for doc in docs
    ]


def delete_entry(entry_id):
    db.collection("journal").document(entry_id).delete()


def update_entry(entry_id, updated_entry):
    db.collection("journal").document(entry_id).update({"entry": updated_entry})


def create_pdf(entries):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    for entry in entries:
        pdf.cell(0, 10, f"Date: {entry['date']}", ln=True)
        pdf.multi_cell(0, 10, f"Entry: {entry['entry']}\n", border=0, align="L")
        if "optimistic_message" in entry and entry["optimistic_message"]:
            pdf.multi_cell(0, 10, f"Message: {entry['optimistic_message']}\n", border=0, align="L")
    return pdf.output(dest="S").encode("latin1")



def generate_optimistic_message(entry):
    try:
        prompt = f"Read the following journal entry and provide a kind, thoughtful comment:\n{user_entry}"
        response = model.generate_content(prompt)
        return response.text.strip().split('.')[0] + "."
    except Exception as e:
        #return f"Could not generate a response due to an error: {e}\"
        return "I'm here for you.keep writing!"
# Journal Page Function
def display_journal():
    st.title("MindHaven's Journal 📓")

    # Back to Home Button
    if st.button("Back to Home"):
        st.session_state.current_page = "welcome"

    # Journal Input Section
    with st.form(key="journal_form"):
        journal_entry = st.text_area("Write your thoughts:", placeholder="Write about your day...")
        submit_button = st.form_submit_button("Add Entry")

        if submit_button:
            if journal_entry.strip():
                # Generate optimistic message using Gemini AI
                with st.spinner("Generating an optimistic response..."):
                    optimistic_message = generate_optimistic_message(journal_entry)

                # Add entry and message to Firestore
                add_entry_to_firestore(journal_entry, optimistic_message)
                st.success("Journal entry added successfully!")
                st.markdown(f"### {optimistic_message}")
            else:
                st.error("Entry cannot be empty.")

    # Display Past Journal Entries
    st.subheader("Past Entries")
    entries = get_entries_from_firestore()

    if entries:
        for entry in entries:
            with st.expander(f"Entry from {entry['date'][:10]}"):
                st.markdown(f"**{entry['entry']}**")
                if entry.get("optimistic_message"):
                    st.markdown(f"*Optimistic Message:* {entry['optimistic_message']}")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Modify", key=f"modify_{entry['id']}"):
                        with st.form(f"form_{entry['id']}"):
                            new_text = st.text_area("Edit your entry:", value=entry["entry"], key=f"text_{entry['id']}")
                            save_button = st.form_submit_button("Save Changes")
                            if save_button:
                                update_entry(entry["id"], new_text)
                                st.success("Entry updated successfully!")
                                st.rerun()
                with col2:
                    if st.button("Delete", key=f"delete_{entry['id']}"):
                        delete_entry(entry["id"])
                        st.rerun()
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
'''