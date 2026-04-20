import streamlit as st
import pandas as pd

from src.risk_engine import compute_risk, build_recommendations, weights as WEIGHTS

st.set_page_config(layout="wide")

st.title("Recommendations")

# -----------------------
# DATA LOAD
# -----------------------
vals = st.session_state.get("vals")
if not vals:
    st.warning("No data loaded. Go to **Home** and click **Fetch current data**.")
    st.stop()

n_med = st.session_state.get("n_med", 0)
out = compute_risk(vals, n_med)

category = out["category"]
final_score = out["final_score"]
dominant = out["dominant"]
sub = out["sub"]
weighted = out["weighted"]
pollen_max = out.get("pollen_max")

# -----------------------
# KPI SUMMARY
# -----------------------
c1, c2, c3 = st.columns(3)

c1.metric("Risk Category", category)
c2.metric("Score (0–10)", f"{final_score:.1f}")
c3.metric("Primary Driver", dominant.capitalize())

# -----------------------
# DISCLAIMER (SEPARATE + PROMINENT)
# -----------------------
st.warning(
    "This tool provides an environmental risk signal only. "
    "It does not diagnose asthma or replace medical advice. "
    "Always follow your prescribed asthma management plan."
)

# -----------------------
# ACTIONABLE GUIDANCE
# -----------------------
st.subheader("Recommended Actions")

# Generate base recommendations
recs = build_recommendations(category, dominant, vals, pollen_max)

# Index 0 is the disclaimer — already shown via st.warning() above
general_recs = recs[1:3]
specific_recs = recs[3:]

col1, col2 = st.columns(2)

# General advice (based on risk level)
with col1:
    st.markdown("### General Guidance")

    for r in general_recs:
        st.write(f"- {r}")

# Factor-specific advice (based on dominant trigger)
with col2:
    st.markdown("### Trigger-Specific Guidance")

    st.write(f"**Dominant factor: {dominant.capitalize()}**")

    for r in specific_recs:
        st.write(f"- {r}")

# -----------------------
# WHY THIS RESULT
# -----------------------
st.divider()
st.subheader("Why this result")

df = pd.DataFrame(
    {
        "Factor": list(sub.keys()),
        "Sub Index (0–10)": [sub[k] for k in sub.keys()],
        "Weight": [WEIGHTS[k] for k in sub.keys()],
        "Weighted Score": [round(weighted[k], 2) for k in sub.keys()],
    }
).sort_values("Weighted Score", ascending=False)

# Highlight dominant factor
def highlight_dom(val):
    if val == dominant:
        return "background-color: #ffcccc"
    return ""

st.dataframe(
    df.style.applymap(highlight_dom, subset=["Factor"]),
    use_container_width=True
)

# -----------------------
# QUICK INSIGHT BOX
# -----------------------
top_factor = df.iloc[0]

st.info(
    f"The current risk is primarily driven by **{top_factor['Factor']}**, "
    f"with a weighted contribution of **{top_factor['Weighted Score']}**."
)

# -----------------------
# CONTEXTUAL CONDITIONS
# -----------------------
st.divider()
st.subheader("Current Conditions")

c1, c2, c3, c4 = st.columns(4)

c1.metric("Temp (°C)", f"{vals.get('temp_c'):.1f}" if vals.get("temp_c") else "N/A")
c2.metric("Humidity (%)", f"{vals.get('rh'):.0f}" if vals.get("rh") else "N/A")
c3.metric("Wind (m/s)", f"{vals.get('wind'):.1f}" if vals.get("wind") else "N/A")
c4.metric("EU AQI", vals.get("eu_aqi") if vals.get("eu_aqi") else "N/A")

# -----------------------
# TRUSTED SOURCES
# -----------------------
st.divider()
st.subheader("Further Guidance")

st.markdown("- NHS asthma guidance: https://www.nhs.uk/conditions/asthma/")
st.markdown("- Asthma + Lung UK (triggers): https://www.asthmaandlung.org.uk/")
st.markdown("- UK Air (air pollution): https://uk-air.defra.gov.uk/")