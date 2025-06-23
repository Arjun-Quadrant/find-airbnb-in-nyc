import streamlit as st

st.set_page_config(page_title="Airbnb Finder", layout="centered")

st.title("Find Top Airbnb Listings in NYC")

st.header("Please adjust the below filters according to your preferences", divider="gray")

with st.form("airbnb_form"):
    safety = st.selectbox("Safety", ["", "Very safe", "Moderately safe", "Don't care"])

    subway = st.selectbox("Subway", ["", "High accessibility", "Medium accessibility", "Low accessibility"])

    room_type = st.multiselect("Room Type", ["Home/Apartment", "Shared room", "Private room", "Hotel room"])

    price = st.selectbox("Price Range", ["", "$0 - $100", "$100 - $500", "$500 - $5000", "$5000 - $20000"])
    no_price = st.selectbox("Do you want to include listings for which no price is listed?", ["Yes", "No"])

    top_n = st.slider("Top N Listings", 1, 20, 5)
    submitted = st.form_submit_button("Find Listings")

    if submitted:
        if not (safety and subway and room_type and price):
            st.warning("Please complete all fields.")
        else:
            # Store inputs in session_state
            st.session_state["safety"] = safety
            st.session_state["subway"] = subway
            st.session_state["room_type"] = room_type
            st.session_state["price"] = price
            st.session_state["no_price"] = no_price
            st.session_state["top_n"] = top_n

            # Navigate to results page
            st.switch_page("pages/1_Results.py")