import streamlit as st
from datetime import datetime
from firebase_admin import credentials, firestore, initialize_app
from firebase_admin import _apps  # Import _apps for checking existing instances

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

# Streamlit App
st.title("MindHaven's Journal")

st.sidebar.title("Navigation")
menu = st.sidebar.radio("Go to:", ["Chatbot", "Journal"])

if menu == "Chatbot":
    st.subheader("Chatbot Section")
    st.write("Your chatbot will be here.")

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
