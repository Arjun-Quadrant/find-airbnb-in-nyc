import streamlit as st

st.markdown("""
    <style>
        [data-testid="stSidebar"] {
            display: none;
        }
        [data-testid="collapsedControl"] {
            display: none;
        }
    </style>
""", unsafe_allow_html=True)

query = st.text_input("Search", "")
if query:
    st.session_state["query"] = query
    st.switch_page("pages/2_Chatbot_Results.py")

# Back link
if st.button("🔙 Back to Home Page"):
    st.switch_page("Home.py")