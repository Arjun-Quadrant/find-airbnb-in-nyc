import streamlit as st
import psycopg2
import os
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

st.header("Please type your query below to look for listings", divider="gray")

conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )
cursor = conn.cursor()

def query_airbnb(input):
    query = sql.SQL(f"""
        SELECT DISTINCT a.id, a.name, a.price, a.longitude, a.latitude, embedding <=> azure_openai.create_embeddings('{os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME")}', '{input}')::vector AS score
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

with st.form("airbnb_form"):
    input = st.text_input("Search", "")
    submitted = st.form_submit_button("Find Listings")
    if submitted:
        st.session_state["rows"] = query_airbnb(input)
        st.switch_page("pages/3_Results.py")

# Back link
if st.button("🔙 Back to Home Page"):
    st.switch_page("Home.py")