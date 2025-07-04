from dotenv import load_dotenv
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

# Ensure previous state exists
if "rows" not in st.session_state:
    st.error("No search data found. Please start from the home page.")
    st.stop()

st.title("Top Airbnb Listings")

results = st.session_state.rows

# Show results
if not results:
    st.warning("No listings found.")
else:
    for i, row in enumerate(results):
        # Should I filter out "bad" matches
        if len(row) == 5 and row[4] >= 0.30:
            continue
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
if st.button("🔙 Back to Home Page"):
    st.switch_page("Home.py")