import streamlit as st
import psycopg2
import re
import os
import pandas as pd
import folium
from psycopg2 import sql
from dotenv import load_dotenv
from streamlit_folium import st_folium

load_dotenv()

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

safety_q1 = int(df.quantile(0.33))
safety_q2 = int(df.quantile(0.66))
max_safety = int(df.max())

sql_str = "SELECT nearby_subway_count AS count FROM subway_listings"
cursor.execute(sql_str)
df = pd.DataFrame(cursor.fetchall())

subway_q1 = int(df.quantile(0.33))
subway_q2 = int(df.quantile(0.66))
max_subway = int(df.max())

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
        SELECT DISTINCT a.id, a.name, a.longitude, a.latitude 
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

# Ensure previous state exists
if "safety" not in st.session_state:
    st.error("No search data found. Please start from the home page.")
    st.stop()

st.title("Top Airbnb Listings")

# Query DB
results = query_airbnb(
    st.session_state.neighborhood,
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
    for i, row in enumerate(results):
        print(results)
        st.write("Listing ID: ", row[0])
        st.write("Listing Name: ", row[1])
        st.markdown("---")

m = folium.Map(location=[40.7128, -74.0060], zoom_start=12)
for row in results:
    id, name, lon, lat = row
    folium.Marker(
        location=[lat, lon],
        popup=f"<b>{id}</b><br>{name}<br>",
        icon=folium.Icon(color="green")
    ).add_to(m)
st_folium(m, width=1200, height=600)

# Back link
if st.button("🔙 Back to Search"):
    st.switch_page("Home.py")