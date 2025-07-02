import streamlit as st
from streamlit_extras.stylable_container import stylable_container

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

st.set_page_config(page_title="Airbnb Finder", layout="centered")

st.title("Find Top Airbnb Listings in NYC")

st.header("Choose a format")

col1, col2 = st.columns(2)

with col1:
    with stylable_container(
        "green",
        css_styles="""
        button {
            background-color: 808080;
            color: black;
        }""",
    ):
        if st.button("Chatbot"):
            st.switch_page("pages/1_Chatbot.py")
with col2:
    with stylable_container(
        "blue",
        css_styles="""
        button {
            background-color: 808080;
            color: black;
        }""",
    ):
        if st.button("Filters"):
            st.switch_page("pages/2_Filters.py")