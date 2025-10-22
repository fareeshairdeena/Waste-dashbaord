import streamlit as st
import folium
from streamlit_folium import st_folium
import sqlite3

# Connect to database
conn = sqlite3.connect("hotspots.db")
cur = conn.cursor()
cur.execute("SELECT * FROM hotspots")
rows = cur.fetchall()

st.title("🚯 Hostpot Sampah Haram Dashboard")

m = folium.Map(location=[2.86, 101.68], zoom_start=13)

for row in rows:
    id_, name, lat, lon, status, notes, image_file = row
    html = f"""
    <b>{name}</b><br>
    <i>{status}</i><br>
    Notes: {notes}<br>
    <img src="{image_file}" width="200">
    """
    folium.Marker([lat, lon], popup=html).add_to(m)

st_data = st_folium(m, width=700, height=500)
