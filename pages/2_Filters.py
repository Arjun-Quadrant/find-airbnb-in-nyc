import streamlit as st
import os
import pandas as pd
import psycopg2
import re
from psycopg2 import sql

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

st.header("Please adjust the below filters according to your preferences", divider="gray")

conn = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD")
)
cursor = conn.cursor()

sql_str = "SELECT nearby_homicide_count AS safety FROM homicide_listings"
cursor.execute(sql_str)
df = pd.DataFrame(cursor.fetchall())

safety_q1 = int(df.quantile(0.33).iloc[0])
safety_q2 = int(df.quantile(0.66).iloc[0])
max_safety = int(df.max().iloc[0])

sql_str = "SELECT nearby_subway_count AS count FROM subway_listings"
cursor.execute(sql_str)
df = pd.DataFrame(cursor.fetchall())

subway_q1 = int(df.quantile(0.33).iloc[0])
subway_q2 = int(df.quantile(0.66).iloc[0])
max_subway = int(df.max().iloc[0])

@st.cache_data(ttl=3600)
def load_neighborhoods():
    sql_str = "SELECT DISTINCT neighbourhood FROM nyc_listings_bnb ORDER BY neighbourhood"
    cursor.execute(sql_str)
    df = pd.DataFrame(cursor.fetchall(), columns=["name"])
    return df["name"].tolist()

def query_airbnb(neighborhood, safety, subway, room_type, price, no_price, top_n):
    safety_bar = 0
    if safety == "Very safe":
        safety_bar = safety_q1
    elif safety == "Moderately safe":
        safety_bar = safety_q2
    elif safety == "Don't care":
        safety_bar = max_safety

    subway_bar = 0
    if subway == "High accessibility":
        subway_bar = subway_q2
    
    elif subway == "Medium accessibility":
        subway_bar = subway_q1
    
    elif subway == "Low accessibility":
        subway_bar = 0

    matches = re.findall(r'\$(\d+)', price)

    # Convert to integers
    min_price, max_price = map(int, matches)

    include_nulls = True if no_price == "Yes" else False

    query = sql.SQL("""
        SELECT DISTINCT a.id, a.name, a.price, a.longitude, a.latitude 
        FROM nyc_listings_bnb a
        JOIN homicide_listings h ON h.name = a.name
        JOIN subway_listings s ON s.name = h.name
        WHERE h.nearby_homicide_count <= %s
          AND s.nearby_subway_count >= %s
          AND a.room_type = ANY(%s)
          AND ((%s AND a.price IS NULL) OR a.price >= CAST(%s AS MONEY) AND a.price <= CAST(%s AS MONEY))
          AND a.neighbourhood = %s
        LIMIT %s
    """)
    
    cursor.execute(query, (
        safety_bar,
        subway_bar,
        room_type,
        include_nulls,
        min_price,
        max_price,
        neighborhood,
        top_n
    ))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

with st.form("airbnb_form"):
    neighborhoods = load_neighborhoods()
    neighborhood = st.selectbox("Select Neighborhood", [""] + neighborhoods)

    safety = st.selectbox("Safety", ["", "Very safe", "Moderately safe", "Don't care"])

    subway = st.selectbox("Subway", ["", "High accessibility", "Medium accessibility", "Low accessibility"])

    room_type = st.multiselect("Room Type", ["Home/Apartment", "Shared room", "Private room", "Hotel room"])

    query = "SELECT price::numeric::float AS price FROM nyc_listings_bnb WHERE price IS NOT NULL"
    cursor.execute(query)
    df = pd.DataFrame(cursor.fetchall())
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
            st.session_state["rows"] = query_airbnb(neighborhood, safety, subway, room_type, price, no_price, top_n)
            # Navigate to results page
            st.switch_page("pages/3_Results.py")

# Back link
if st.button("🔙 Back to Home Page"):
    st.switch_page("Home.py")