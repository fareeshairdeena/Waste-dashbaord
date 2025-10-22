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
    # Image folder path
    img_path = os.path.join("Images", filename)
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
# 5️⃣ Sidebar selection
# ============================================================
st.sidebar.header("🔍 Hotspot Selection")
selected = st.sidebar.selectbox("Select a Hotspot to Zoom:", df["name"])
selected_row = df[df["name"] == selected].iloc[0]

# ============================================================
# 6️⃣ Create base map (Google Earth view)
# ============================================================
m = folium.Map(
    location=[selected_row["latitude"], selected_row["longitude"]],
    zoom_start=17,  # zoom in closer to selected hotspot
    tiles='https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',
    attr='Google Earth Satellite'
)

# Add all hotspot markers
for _, row in df.iterrows():
    popup_html = f"""
    <b>{row['name']}</b><br>
    <i>{row['status']}</i><br>
    Notes: {row['notes']}<br>
    """
    icon_color = "green" if row["name"] == selected else "red"
    folium.Marker(
        location=[row["latitude"], row["longitude"]],
        popup=popup_html,
        tooltip=row["name"],
        icon=folium.Icon(color=icon_color, icon="info-sign"),
    ).add_to(m)

# Add map to Streamlit
st.subheader("🗺️ Hotspot Location")
map_data = st_folium(m, width=900, height=550, key=selected)

# ============================================================
# 7️⃣ Display image + details
# ============================================================
st.subheader("📷 Hotspot Details")

col1, col2 = st.columns([1, 2])
with col1:
    image = load_image(selected_row["image_file"])
    if image:
        st.image(image, caption=selected_row["name"], use_container_width=True)
with col2:
    st.markdown(f"""
    ### 🏷️ {selected_row['name']}
    - **Latitude:** {selected_row['latitude']}
    - **Longitude:** {selected_row['longitude']}
    - **Status:** {selected_row['status']}
    - **Notes:** {selected_row['notes']}
    """)

# ============================================================
# 8️⃣ Display table view (optional but useful)
# ============================================================
st.markdown("### 📋 Hotspots Summary")
st.dataframe(df[["name", "latitude", "longitude", "status", "notes"]])

st.markdown("---")
st.caption("Developed for Smart Waste Monitoring using IoT & GeoAI 🌍")
