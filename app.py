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
from io import BytesIO

# ============================================================
# 2️⃣ Helper function to load images
# ============================================================
def load_image(filename):
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
selected = st.sidebar.selectbox("Select a Hotspot:", df["name"])
selected_row = df[df["name"] == selected].iloc[0]

# ============================================================
# 6️⃣ Create base map (Google Earth Hybrid)
# ============================================================
m = folium.Map(
    location=[selected_row["latitude"], selected_row["longitude"]],
    zoom_start=17,
    tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}',
    attr='Google Earth Hybrid'
)

# Add all markers
for _, row in df.iterrows():
    popup_html = f"""
    <b>{row['name']}</b><br>
    <i>{row['status']}</i><br>
    {row['notes']}
    """
    color = "green" if row['name'] == selected else "blue"
    folium.Marker(
        location=[row["latitude"], row["longitude"]],
        popup=popup_html,
        icon=folium.Icon(color=color, icon="info-sign"),
    ).add_to(m)

# ============================================================
# 7️⃣ Layout: Map (Left) | Details + Image (Right)
# ============================================================
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("🗺️ Hotspot Map")
    st_folium(m, width=850, height=550, key=selected)

with col2:
    st.subheader("📸 Hotspot Details")
    image = load_image(selected_row["image_file"])
    if image:
        st.image(image, caption=selected_row["name"], use_container_width=True)

    st.markdown(f"""
    ### 🏷️ {selected_row['name']}
    - **Latitude:** {selected_row['latitude']}
    - **Longitude:** {selected_row['longitude']}
    - **Status:** {selected_row['status']}
    - **Notes:** {selected_row['notes']}
    """)

# ============================================================
# 8️⃣ Table view + Download option
# ============================================================
st.markdown("---")
st.subheader("📋 Hotspots Summary Table")

# Show number of hotspots
st.write(f"**Total Hotspots:** {len(df)}")

# Display table
st.dataframe(df[["name", "latitude", "longitude", "status", "notes"]], use_container_width=True)

# Download button for Excel
output = BytesIO()
with pd.ExcelWriter(output, engine='openpyxl') as writer:
    df.to_excel(writer, index=False, sheet_name='Hotspots')
excel_data = output.getvalue()

st.download_button(
    label="📥 Download Table as Excel",
    data=excel_data,
    file_name="hotspot_summary.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# ============================================================
# 9️⃣ Footer
# ============================================================
st.markdown("---")
st.caption("Developed for Smart Waste Monitoring using IoT & GeoAI 🌍")
