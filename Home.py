import streamlit as st
import psycopg2
import os
import pandas as pd

st.set_page_config(page_title="Airbnb Finder", layout="centered")

st.title("Find Top Airbnb Listings in NYC")

st.header("Please adjust the below filters according to your preferences", divider="gray")

conn = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD")
)
cursor = conn.cursor()

@st.cache_data(ttl=3600)
def load_neighborhoods():
    sql_str = "SELECT DISTINCT neighbourhood FROM nyc_listings_bnb ORDER BY neighbourhood"
    cursor.execute(sql_str)
    df = pd.DataFrame(cursor.fetchall(), columns=["name"])
    return df["name"].tolist()

with st.form("airbnb_form"):

    neighborhoods = load_neighborhoods()
    neighborhood = st.selectbox("Select Neighborhood", [""] + neighborhoods)

    safety = st.selectbox("Safety", ["", "Very safe", "Moderately safe", "Don't care"])

    subway = st.selectbox("Subway", ["", "High accessibility", "Medium accessibility", "Low accessibility"])

    room_type = st.multiselect("Room Type", ["Home/Apartment", "Shared room", "Private room", "Hotel room"])

    sql = "SELECT price::numeric::float AS price FROM nyc_listings_bnb WHERE price IS NOT NULL"
    cursor.execute(sql)
    df = pd.DataFrame(cursor.fetchall())
    cursor.close()
    price_q1 = int(df.quantile(0.25).iloc[0])
    price_q2 = int(df.quantile(0.5).iloc[0])
    price_q3 = int(df.quantile(0.75).iloc[0])
    max_price = int(df.max().iloc[0])

    price = st.selectbox("Price Range", ["", f"$0 - ${price_q1}", f"${price_q1} - ${price_q2}", f"${price_q2} - ${price_q3}", f"${price_q3} - ${max_price}"])
    no_price = st.selectbox("Do you want to include listings for which no price is listed?", ["Yes", "No"])

    top_n = st.slider("Top N Listings", 1, 20, 5)
    submitted = st.form_submit_button("Find Listings")

    if submitted:
        if not (neighborhood and safety and subway and room_type and price):
            st.warning("Please complete all fields.")
        else:
            # Store inputs in session_state
            st.session_state["neighborhood"] = neighborhood
            st.session_state["safety"] = safety
            st.session_state["subway"] = subway
            st.session_state["room_type"] = room_type
            st.session_state["price"] = price
            st.session_state["no_price"] = no_price
            st.session_state["top_n"] = top_n

            # Navigate to results page
            st.switch_page("pages/1_Results.py")