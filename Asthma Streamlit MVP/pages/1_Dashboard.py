import streamlit as st
import pandas as pd

from src.risk_engine import compute_risk, WEIGHTS

st.title("Dashboard")
st.caption("Summary of current environmental risk index. Informational only — not diagnosis.")

vals = st.session_state.get("vals")
if not vals:
    st.warning("No data loaded. Go to **Home** and click **Fetch current data**.")
    st.stop()

n_med = st.session_state.get("n_med", 0)
out = compute_risk(vals, n_med)

category = out["category"]
final_score = out["final_score"]
dominant = out["dominant"]
A = out["amplifier"]
sub = out["sub"]
weighted = out["weighted"]

k1, k2, k3, k4 = st.columns(4)
k1.metric("Risk Category", category)
k2.metric("Final Score (0–10)", f"{final_score:.1f}")
k3.metric("Dominant Factor", dominant)
k4.metric("Medical Amplifier", f"x{A:.1f}")

st.write("**Risk level**")
st.progress(min(final_score / 10.0, 1.0))
st.caption("Score uses a weighted-dominant factor model. Final score = min(10, amplifier × base_score).")

left, right = st.columns([1.25, 1.0])

with left:
    st.subheader("Factor Breakdown")

    df = pd.DataFrame(
        {
            "factor": list(sub.keys()),
            "sub_index_0_10": [sub[k] for k in sub.keys()],
            "weight": [WEIGHTS[k] for k in sub.keys()],
            "weighted_score": [round(weighted[k], 2) for k in sub.keys()],
        }
    ).sort_values("weighted_score", ascending=False)

    st.dataframe(df, use_container_width=True)
    st.bar_chart(df.set_index("factor")[["weighted_score"]])

with right:
    st.subheader("Notes")
    st.write(f"- Timestamp: **{vals.get('time')}**")
    st.write("- Informational only. Not diagnosis.")
    st.write("- Environmental risk indicator (not a clinical outcome prediction).")

st.info("Next: open **Recommendations** in the sidebar.")
