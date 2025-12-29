import streamlit as st
import pandas as pd

from src.risk_engine import compute_risk, build_recommendations, weights as WEIGHTS

st.title("Recommendations")
st.caption("Informational only. Not diagnosis. Follow your personal asthma plan and clinical advice.")

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

c1, c2, c3 = st.columns(3)
c1.metric("Risk Category", category)
c2.metric("Final Score (0–10)", f"{final_score:.1f}")
c3.metric("Dominant Factor", dominant)

st.subheader("What to do today")
recs = build_recommendations(category, dominant, vals, pollen_max)
for r in recs:
    st.write(f"- {r}")

st.divider()
st.subheader("Why you got this result")

df = pd.DataFrame(
    {
        "factor": list(sub.keys()),
        "sub_index_0_10": [sub[k] for k in sub.keys()],
        "weight": [WEIGHTS[k] for k in sub.keys()],
        "weighted_score": [round(weighted[k], 2) for k in sub.keys()],
    }
).sort_values("weighted_score", ascending=False)

st.dataframe(df, use_container_width=True)

st.subheader("Useful links")
st.markdown("- NHS asthma guidance: https://www.nhs.uk/conditions/asthma/")
st.markdown("- Asthma + Lung UK (triggers): https://www.asthmaandlung.org.uk/conditions/asthma/asthma-triggers")
st.markdown("- UK Air (air pollution): https://uk-air.defra.gov.uk/")

st.info("This tool provides an environmental risk signal only. It does not diagnose asthma or replace medical advice.")
