import os, sys
sys.path.append(os.path.dirname(__file__))
import streamlit as st
st.set_page_config(
    page_title="Asthma Risk Precautions System",
    layout="centered"
)
try:
    from streamlit_geolocation import geolocation # pip install streamlit-geolocation
except Exception:
    streamlit_geolocation = None
    st.warning("streamlit-geolocation package not found. Geolocation features will be disabled.")
from src.openmeteo_client import fetch_openmeteo_current
st.title ("Asthma Environmental Risk Index")
st.caption("Rule-based environmental decision support. Informational only — not diagnosis or clinical prediction.")
st.sidebar.header("Controls")

geo = None 
if streamlit_geolocation is not None:
    geo = geolocation.get_geolocation()

has_geo = bool(geo and geo.get("latitude") is not None and geo.get("longitude") is not None)
lat_default = float(geo["latitude"]) if has_geo else 51.5074  # London default
lon_default = float(geo["longitude"]) if has_geo else -0.1278  # London default

lat = st.sidebar.number_input("Latitude", value=float(lat_default), format="%.6f")
lon = st.sidebar.number_input("Longitude", value=float(lon_default), format="%.6f")

st.sidebar.subheader("Medical amplifier (optional)")
f1 = st.sidebar.checkbox("History of severe attacks / hospitalisation (self-reported)")
f2 = st.sidebar.checkbox("Recent symptoms / flare-up (self-reported)")
f3 = st.sidebar.checkbox("Poor control / frequent reliever use (self-reported)")

st.session_state["n_med"] = int(f1) + int(f2) + int(f3)

@st.cache_data(ttl=600)
def cached_fetch(lat_: float, lon_: float) -> dict:
    return fetch_openmeteo_current(lat_, lon_)

if st.sidebar.button("Fetch current data"):
    try:
        st.session_state["vals"] = cached_fetch(float(lat), float(lon))
        st.sidebar.success("Fetched.")
    except Exception as e:
        st.sidebar.error(f"Fetch failed: {e}")

vals = st.session_state.get("vals")
if not vals:
    st.info("Use the sidebar to set location and click **Fetch current data**.")
    st.stop()

st.success("Data loaded. Use the left menu to open **Dashboard** and **Recommendations**.")
st.write(f"Timestamp: `{vals.get('time')}`")

with st.expander("Show current inputs"):
    st.json(vals)