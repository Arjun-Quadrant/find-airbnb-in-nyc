from dotenv import load_dotenv
from psycopg2 import sql
import psycopg2
import os
import folium
import streamlit as st
from streamlit_folium import st_folium

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

load_dotenv()

conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )
cursor = conn.cursor()

def query_airbnb(input):
    query = sql.SQL(f"""
        SELECT DISTINCT a.id, a.name, embedding <=> azure_openai.create_embeddings('{os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME")}', '{input}')::vector AS score, a.longitude, a.latitude
        FROM all_listing_data a
        ORDER BY embedding <=> azure_openai.create_embeddings('{os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME")}', '{input}')::vector
        LIMIT 10;
    """)
    
    cursor.execute(query, (
        input
    ))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

# Ensure previous state exists
if "query" not in st.session_state:
    st.error("No search data found. Please start from the home page.")
    st.stop()

st.title("Top Airbnb Listings")

results = query_airbnb(
    st.session_state.query
)

# Show results
if not results:
    st.warning("No listings found.")
else:
    for i, row in enumerate(results):
        # Should I filter out "bad" matches
        if row[2] < 0.30:
            st.write("Listing ID: ", row[0])
            st.write("Listing Name: ", row[1])
            st.write("Listing Score: ", row[2])
            st.markdown("---")

m = folium.Map(location=[40.7128, -74.0060], zoom_start=12)
for row in results:
    id, name, _, lon, lat = row
    folium.Marker(
        location=[lat, lon],
        popup=f"<b>{id}</b><br>{name}<br>",
        icon=folium.Icon(color="green")
    ).add_to(m)
st_folium(m, width=1200, height=600)

# Back link
if st.button("🔙 Back to Search"):
    st.switch_page("1_Chatbot.py")