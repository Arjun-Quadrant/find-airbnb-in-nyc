import streamlit as st
import psycopg2
import re
import os
from psycopg2 import sql
from dotenv import load_dotenv

load_dotenv()

def query_airbnb(safety, subway, room_type, price, no_price, top_n):

    safety_bar = 0
    if safety == "Very safe":
        safety_bar = 5
    elif safety == "Moderately safe":
        safety_bar = 10
    elif safety == "Don't care":
        safety_bar = 100

    subway_bar = 0
    if subway == "High accessibility":
        subway_bar = 6
    
    elif subway == "Medium accessibility":
        subway_bar = 3
    
    elif subway == "Low accessibility":
        subway_bar = 0

    matches = re.findall(r'\$(\d+)', price)
    # Convert to integers
    min_price, max_price = map(int, matches)

    include_nulls = True if no_price == "Yes" else False

    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )
    cursor = conn.cursor()

    query = sql.SQL("""
        SELECT DISTINCT a.id, a.name 
        FROM nyc_listings_bnb a
        JOIN homicide_listings h ON h.name = a.name
        JOIN subway_listings s ON s.name = h.name
        WHERE h.nearby_homicide_count <= %s
          AND s.nearby_station_count >= %s
          AND a.room_type = ANY(%s)
          AND ((%s AND a.price IS NULL) OR a.price >= CAST(%s AS MONEY) AND a.price <= CAST(%s AS MONEY))
        LIMIT %s
    """)
    
    cursor.execute(query, (
        safety_bar,
        subway_bar,
        room_type,
        include_nulls,
        min_price,
        max_price,
        top_n
    ))
    rows = cursor.fetchall()

    cursor.close()
    conn.close()
    return rows

# Ensure previous state exists
if "safety" not in st.session_state:
    st.error("No search data found. Please start from the home page.")
    st.stop()

st.title("Top Airbnb Listings")

# Query DB
results = query_airbnb(
    st.session_state.safety,
    st.session_state.subway,
    st.session_state.room_type,
    st.session_state.price,
    st.session_state.no_price,
    st.session_state.top_n
)

# Show results
if not results:
    st.warning("No listings found.")
else:
    for i, row in enumerate(results, 1):
        print(results)
        st.write("Listing ID: ", row[0])
        st.write("Listing Name: ", row[1])
        st.markdown("---")

# Back link
if st.button("🔙 Back to Search"):
    st.switch_page("Home.py")