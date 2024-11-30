import streamlit as st

# Set the page title and layout
st.set_page_config(page_title="MindHaven", page_icon="🧠", layout="centered")

# Custom Styles
st.markdown("""
    <style>
        .welcome-container {
            text-align: center;
            margin-top: 50px;
        }
        .welcome-logo {
            margin: 20px auto;
            width: 200px;
            height: auto;
        }
        .button-container {
            display: flex;
            justify-content: center;
            gap: 20px;
            margin-top: 30px;
        }
    </style>
""", unsafe_allow_html=True)

# Main Container
with st.container():
    st.markdown("<div class='welcome-container'>", unsafe_allow_html=True)
    st.image("logo.png", caption="MindHaven", width=200, class_="welcome-logo")  # Replace "logo.png" with your logo file
    st.markdown("## Welcome to MindHaven 🧠")
    st.markdown("Your supportive mental health companion.")

    # Navigation Buttons
    col1, col2 = st.columns([1, 1])
    with col1:
        st.button("Go to Journal", key="journal_button", on_click=lambda: st.experimental_set_query_params(page="journal"))
    with col2:
        st.button("Go to Chatbot", key="chatbot_button", on_click=lambda: st.experimental_set_query_params(page="chatbot"))
