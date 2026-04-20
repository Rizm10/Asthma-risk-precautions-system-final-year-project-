import streamlit as st
import pandas as pd

from src.risk_engine import compute_risk, weights

# Configure wide layout for better data visibility
st.set_page_config(layout="wide")

st.title("Asthma Environmental Risk Dashboard")
st.caption("Real-time environmental risk index. Interpret results alongside your asthma management plan.")

# Retrieve environmental data stored from Home page
vals = st.session_state.get("vals")
if not vals:
    st.warning("No data loaded. Go to **Home** and click **Fetch current data**.")
    st.stop()

# Retrieve optional medical modifiers (used for amplification)
n_med = st.session_state.get("n_med", 0)

# Compute full risk output using core engine
out = compute_risk(vals, n_med)

# Extract key outputs for display
category = out["category"]
final_score = out["final_score"]
dominant = out["dominant"]
A = out["amplifier"]
sub = out["sub"]
weighted = out["weighted"]

# -----------------------
# KPI SECTION
# -----------------------
# Displays high-level summary of the system output
k1, k2, k3, k4 = st.columns(4)

k1.metric("Risk Category", category)
k2.metric("Score (0–10)", f"{final_score:.1f}")
k3.metric("Dominant Trigger", dominant.capitalize())
k4.metric("Amplifier", f"x{A:.1f}")

# -----------------------
# RISK VISUALISATION
# -----------------------
# Converts numerical score into a visual severity indicator
st.markdown("### Risk Level")

progress_val = min(final_score / 10.0, 1.0)

# Conditional colouring improves interpretability of severity
if final_score < 3:
    st.success("Low environmental risk")
elif final_score < 6:
    st.warning("Moderate environmental risk")
else:
    st.error("High environmental risk")

st.progress(progress_val)

# -----------------------
# MAIN LAYOUT SPLIT
# -----------------------
left, right = st.columns([1.3, 1])

# -----------------------
# FACTOR BREAKDOWN (LEFT)
# -----------------------
with left:
    st.subheader("Factor Breakdown")

    # Create structured table linking sub-indices to weighted contribution
    df = pd.DataFrame(
        {
            "Factor": list(sub.keys()),
            "Sub Index (0–10)": [sub[k] for k in sub.keys()],
            "Weight": [weights[k] for k in sub.keys()],
            "Weighted Score": [round(weighted[k], 2) for k in sub.keys()],
        }
    ).sort_values("Weighted Score", ascending=False)

    # Highlight dominant factor to emphasise interpretability
    def highlight_dom(val):
        if val == dominant:
            return "background-color: #ffcccc"
        return ""

    st.dataframe(
        import requests

WEATHER_URL = "https://api.open-meteo.com/v1/forecast"
AIR_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"


def _get_json(url: str, params: dict) -> dict:
    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()
    return r.json()


def fetch_openmeteo_current(lat: float, lon: float) -> dict:
    # Weather (current)
    w_params = {
        "latitude": lat,
        "longitude": lon,
        "timezone": "auto",
        "current": "temperature_2m,relative_humidity_2m,wind_speed_10m",
    }
    w = _get_json(WEATHER_URL, w_params)
    wc = (w or {}).get("current") or {}

    # Air quality + pollen (current)
    a_params = {
        "latitude": lat,
        "longitude": lon,
        "timezone": "auto",
        "current": ",".join(
            [
                "european_aqi",
                "pm2_5",
                "nitrogen_dioxide",
                "ozone",
                "alder_pollen",
                "birch_pollen",
                "grass_pollen",
                "mugwort_pollen",
                "olive_pollen",
                "ragweed_pollen",
            ]
        ),
    }
    a = _get_json(AIR_URL, a_params)
    ac = (a or {}).get("current") or {}

    return {
        "time": wc.get("time") or ac.get("time"),
        "temp_c": wc.get("temperature_2m"),
        "rh": wc.get("relative_humidity_2m"),
        "wind": wc.get("wind_speed_10m"),
        "eu_aqi": ac.get("european_aqi"),
        "pm2_5": ac.get("pm2_5"),
        "no2": ac.get("nitrogen_dioxide"),
        "o3": ac.get("ozone"),
        "pollen": {
            "alder": ac.get("alder_pollen"),
            "birch": ac.get("birch_pollen"),
            "grass": ac.get("grass_pollen"),
            "mugwort": ac.get("mugwort_pollen"),
            "olive": ac.get("olive_pollen"),
            "ragweed": ac.get("ragweed_pollen"),
        },
    }


    # Visual comparison of weighted contributions
    st.bar_chart(df.set_index("Factor")[["Weighted Score"]])

# -----------------------
# RAW DATA + INTERPRETATION (RIGHT)
# -----------------------
with right:
    st.subheader("Current Conditions")

    # Displays raw environmental inputs for transparency
    st.metric("Temperature (°C)", f"{vals.get('temp_c'):.1f}" if vals.get("temp_c") else "N/A")
    st.metric("Humidity (%)", f"{vals.get('rh'):.0f}" if vals.get("rh") else "N/A")
    st.metric("Wind (m/s)", f"{vals.get('wind'):.1f}" if vals.get("wind") else "N/A")
    st.metric("EU AQI", vals.get("eu_aqi") if vals.get("eu_aqi") else "N/A")

    st.divider()

    st.subheader("Interpretation")

    # Explicit mapping between model logic and output
    st.write(f"- **Primary driver:** {dominant.capitalize()}")
    st.write(f"- **Base score:** {out['base_score']:.2f}")
    st.write(f"- **Amplified score:** {final_score:.2f}")

    # Makes aggregation logic visible to user
    st.caption("Score = dominant(weight × sub-index) × amplifier")

# -----------------------
# FOOTER
# -----------------------
st.divider()

# Reinforces non-diagnostic framing as a deliberate design decision
st.caption(
    "This system provides an environmental risk signal only. "
    "It does not diagnose asthma or predict medical events."
)

st.info("Next: open **Recommendations** in the sidebar.")