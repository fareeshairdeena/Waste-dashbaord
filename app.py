import streamlit as st
import folium
from streamlit_folium import st_folium
import sqlite3
import pandas as pd
import os
from PIL import Image

# Load image safely
def load_image(filename):
    img_path = os.path.join("images", filename)
    if os.path.exists(img_path):
        return Image.open(img_path)
    else:
        st.warning(f"Image not found: {filename}")
        return None

# --- PAGE SETUP ---
st.set_page_config(page_title="Waste Hotspot Dashboard", layout="wide")
st.title("🚨 Waste Hotspot Monitoring Dashboard")
st.write("Monitor illegal dumping and hotspot areas interactively.")

# --- DATABASE CONNECTION ---
conn = sqlite3.connect("hotspots.db")
df = pd.read_sql_query("SELECT * FROM hotspots", conn)
conn.close()

# --- MAP CREATION ---
m = folium.Map(location=[2.86, 101.68], zoom_start=13)
for _, row in df.iterrows():
    popup_html = f"""
    <b>{row['name']}</b><br>
    <i>{row['status']}</i><br>
    {row['notes']}<br>
    """
    folium.Marker(
        location=[row['latitude'], row['longitude']],
        popup=popup_html,
        icon=folium.Icon(color="red", icon="trash"),
    ).add_to(m)

# --- DISPLAY MAP ---
st.subheader("🗺️ Interactive Hotspot Map")
map_data = st_folium(m, width=800, height=500)

# --- DETAILS SECTION ---
st.subheader("📋 Hotspot Details")

# Create a data table
st.dataframe(df[['id', 'name', 'status', 'notes']], use_container_width=True)

# --- IMAGE + INFO ---
if map_data and map_data.get("last_object_clicked_tooltip"):
    clicked_name = map_data["last_object_clicked_tooltip"]
    st.write(f"Selected: {clicked_name}")

else:
    # let user manually choose
    selected = st.selectbox("Select hotspot:", df["name"])
    info = df[df["name"] == selected].iloc[0]
    
    col1, col2 = st.columns([1, 2])
    with col1:
        img_path = os.path.join("images", info["image_file"])
        if os.path.exists(img_path):
            st.image(img_path, caption=info["name"], use_container_width=True)
        else:
            st.warning("Image not found.")
    with col2:
        st.markdown(f"""
        ### 🏷️ {info['name']}
        - **Latitude:** {info['latitude']}
        - **Longitude:** {info['longitude']}
        - **Status:** {info['status']}
        - **Notes:** {info['notes']}
        """)

st.markdown("---")
st.caption("Developed for Smart Waste Monitoring using IoT & GeoAI")
