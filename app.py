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
# 8️⃣ Table view + Download option (CSV version)
# ============================================================

import streamlit as st
import pandas as pd

st.markdown("---")
st.subheader("📊 Regional Waste Management Data")

# --- Region selection
region = st.selectbox("Select Region:", ["Selangor", "Penang"])

# --- Define file paths (GitHub RAW CSV links)
files = {
    "Selangor": {
        "Aduan JAS 2020–2025": "https://raw.githubusercontent.com/fareeshairdeena/Waste-dashbaord/main/Aduan%20JAS%20Selangor%202020_2025.csv",
        "Bilangan Aduan JAS": "https://raw.githubusercontent.com/fareeshairdeena/Waste-dashbaord/main/Bilangan%20Aduan%20JAS%20Selangor.csv",
        "Hotspot Sampah GIS": "https://raw.githubusercontent.com/fareeshairdeena/Waste-dashbaord/main/Hotspot%20sampah%20GIS%20Selangor.csv"
    },
    "Penang": {
        "Aduan JAS 2020–2025": "https://raw.githubusercontent.com/fareeshairdeena/Waste-dashbaord/main/Aduan%20JAS%20Penang%202020_2025.csv",
        "Bilangan Aduan JAS": "https://raw.githubusercontent.com/fareeshairdeena/Waste-dashbaord/main/Bilangan%20Aduan%20JAS%20Penang.csv",
        "Hotspot Sampah GIS": "https://raw.githubusercontent.com/fareeshairdeena/Waste-dashbaord/main/Hotspot%20sampah%20GIS%20Penang.csv"
    }
}

# --- Safe CSV loader
def load_csv(file_url):
    try:
        return pd.read_csv(file_url)
    except Exception as e:
        st.error(f"⚠️ Error reading file ({file_url}): {e}")
        return pd.DataFrame()

# --- Display each table sequentially
for i, (label, url) in enumerate(files[region].items(), start=1):
    st.markdown("---")
    st.subheader(f"{label} – {region}")

    df = load_csv(url)
    if df.empty:
        st.warning(f"⚠️ Dataset for {label} ({region}) is empty or unreadable.")
        continue

    # Add numbering column
    df.insert(0, "No.", range(1, len(df) + 1))

    # Display data
    st.info(f"📊 Total Records: **{len(df)}**")
    st.dataframe(df, use_container_width=True)

    # Download CSV
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label=f"📥 Download {label} ({region})",
        data=csv,
        file_name=f"{label}_{region}.csv",
        mime="text/csv"
    )

# ============================================================
# 9️⃣ Footer
# ============================================================
st.markdown("---")
st.caption("Developed for Smart Waste Monitoring using IoT & GeoAI 🌍")
