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

# Ensure previous state exists
if "rows" not in st.session_state:
    st.error("No search data found. Please start from the home page.")
    st.stop()

st.title("Top Airbnb Listings")

results = st.session_state.rows

# Visualize results
m = folium.Map(location=[40.7128, -74.0060], zoom_start=12)
for row in results:
    id = row[0]
    name = row[1]
    lon = row[3]
    lat = row[4]
    folium.Marker(
        location=[lat, lon],
        popup=f"<b>{name}</b>",
        icon=folium.Icon(color="green")
    ).add_to(m)
st_folium(m, width=1200, height=600)

# List results
if not results:
    st.warning("No listings found.")
else:
    for i, row in enumerate(results):
        # Should I filter out "bad" matches
        if len(row) == 6 and row[5] >= 0.30:
            continue
        st.write("Listing ID: ", row[0])
        st.write("Listing Name: ", row[1])
        st.write("Price: $", row[2])
        st.markdown("---")

# Back link
if st.button("🔙 Back to Home Page"):
    st.switch_page("Home.py")