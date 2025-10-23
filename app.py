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
# 2️⃣ Page setup
# ============================================================
st.set_page_config(page_title="Waste Hotspot Dashboard", layout="wide")
st.title("🚨 Waste Hotspot Monitoring Dashboard")

# ============================================================
# 3️⃣ Load the database
# ============================================================
conn = sqlite3.connect("hotspots.db")
df = pd.read_sql_query("SELECT * FROM hotspots", conn)
conn.close()

# Ensure your DB has a column like `image_link` (pointing to Imgur or GitHub raw URLs)
# Example: https://raw.githubusercontent.com/username/repo/main/Images/hotspot_a.jpg

# ============================================================
# 4️⃣ Sidebar selection
# ============================================================
st.sidebar.header("🔍 Hotspot Selection")
selected = st.sidebar.selectbox("Select a Hotspot:", df["name"])
selected_row = df[df["name"] == selected].iloc[0]

# ============================================================
# 5️⃣ Create base map (Google Earth Hybrid)
# ============================================================
m = folium.Map(
    location=[selected_row["latitude"], selected_row["longitude"]],
    zoom_start=17,
    tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}',
    attr='Google Maps Hybrid'
)

# Add all hotspot markers
for _, row in df.iterrows():
    popup_html = f"""
    <b>{row['name']}</b><br>
    <i>{row['status']}</i><br>
    {row['notes']}<br>
    """
    folium.Marker(
        location=[row["latitude"], row["longitude"]],
        popup=popup_html,
        icon=folium.Icon(color="blue", icon="info-sign"),
    ).add_to(m)

# Highlight selected hotspot
folium.Marker(
    location=[selected_row["latitude"], selected_row["longitude"]],
    popup=selected_row["name"],
    icon=folium.Icon(color="green", icon="info-sign"),
).add_to(m)

# ============================================================
# 6️⃣ Layout: Map on left, Details on right
# ============================================================
col1, col2 = st.columns([1.3, 1])

with col1:
    st.subheader("🗺️ Hotspot Location")
    st_folium(m, width=900, height=550, key=selected)

with col2:
    st.subheader("📸 Hotspot Details")
    # Show image from Imgur/GitHub
    st.image(selected_row["image_link"], caption=selected_row["name"], use_container_width=True)
    st.markdown(f"""
    ### 🏷️ {selected_row['name']}
    - **Latitude:** {selected_row['latitude']}
    - **Longitude:** {selected_row['longitude']}
    - **Status:** {selected_row['status']}
    - **Notes:** {selected_row['notes']}
    - **Image Link:** [Open Image]({selected_row['image_link']})
    """)

# ============================================================
# 7️⃣ Table view + Download
# ============================================================
st.markdown("### 📋 Hotspots Summary")

# Replace 'image_file' column with 'image_link' in table
table_columns = ["name", "latitude", "longitude", "status", "notes", "image_link"]
st.dataframe(df[table_columns], use_container_width=True)

# Show total count
st.info(f"📊 Total hotspots in database: **{len(df)}**")

# Download as CSV
csv_data = df[table_columns].to_csv(index=False).encode("utf-8")
st.download_button(
    label="📥 Download Table as CSV",
    data=csv_data,
    file_name="hotspots_summary.csv",
    mime="text/csv"
)

st.markdown("---")
st.caption("Developed for Smart Waste Monitoring using IoT & GeoAI 🌍")
