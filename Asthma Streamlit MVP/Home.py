import streamlit as st
try:
    from streamlit_geolocation import geolocation # pip install streamlit-geolocation
except Exception:
    streamlit_geolocation = None
    st.warning("streamlit-geolocation package not found. Geolocation features will be disabled.")
from src.openweather_api import fetch_openmeteo_current_weather

st.config.page_title ( page_title = "Asthma Risk Precautions System" , layoit = "centered" )
st.title ("Asthma Environmental Risk Index")
st.caption("Rule-based environmental decision support. Informational only — not diagnosis or clinical prediction.")
st.sidebar.header("Controls")
