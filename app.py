# ============================================================
# 1️⃣ Import libraries
# ============================================================
import os
import streamlit as st
import folium
from streamlit_folium import st_folium
import sqlite3
import pandas as pd
from PIL import Image

# ============================================================
# 2️⃣ Define helper function to load images
# ============================================================
def load_image(filename):
    # ---- OPTION A: If your images are in a subfolder "images/" ----
    img_path = os.path.join("Images", filename)

    # ---- OPTION B: Uncomment this line if your images are in the same folder ----
    # img_path = filename

    if os.path.exists(img_path):
        return Image.open(img_path)
    else:
        st.warning(f"Image not found: {img_path}")
        return None

# ============================================================
# 3️⃣ Page setup
# ============================================================
st.set_page_config(page_title="Waste Hotspot Dashboard", layout="wide")
st.title("🚨 Waste Hotspot Monitoring Dashboard")

# ============================================================
# 4️⃣ Load the database
# ============================================================
conn = sqlite3.connect("hotspots.db")
df = pd.read_sql_query("SELECT * FROM hotspots", conn)
conn.close()

# ============================================================
# 5️⃣ Create and display map
# ============================================================
# Google Earth-like view (Satellite)
m = folium.Map(
    location=[2.9, 101.6],
    zoom_start=17,
    tiles='https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',
    attr='Google Earth Satellite'
)
for _, row in df.iterrows():
    popup_html = f"""
    <b>{row['name']}</b><br>
    <i>{row['status']}</i><br>
    {row['notes']}<br>
    """
    folium.Marker(
        location=[row['latitude'], row['longitude']],
        popup=popup_html,
        icon=folium.Icon(color="blue", icon="pin location"),
    ).add_to(m)

st.subheader("🗺️ Hotspot Location")
map_data = st_folium(m, width=800, height=500)

# ============================================================
# 6️⃣ Display image + info
# ============================================================
st.subheader("📷 Hotspot Images and Details")
selected = st.selectbox("Select hotspot:", df["name"])

info = df[df["name"] == selected].iloc[0]
col1, col2 = st.columns([1, 2])

with col1:
    image = load_image(info["image_file"])
    if image:
        st.image(image, caption=info["name"], use_container_width=True)

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
