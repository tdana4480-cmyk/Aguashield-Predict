
import streamlit as st
import pandas as pd
import joblib
import json
from pathlib import Path

st.set_page_config(
    page_title="AquaShield Predict",
    page_icon="💧",
    layout="wide"
)

BASE = Path(__file__).parent
model = joblib.load(BASE / "model.pkl")
meta = json.loads((BASE / "metadata.json").read_text(encoding="utf-8"))
ranges = meta["ranges"]

# -----------------------------
# Header
# -----------------------------
st.title("💧 AquaShield Predict")
st.caption("AI-assisted RO membrane performance monitoring — Prototype v2")

st.info(
    "AquaShield Predict estimates expected RO water flux from operating conditions, "
    "then compares it with the observed flux to flag abnormal performance deviation. "
    "A deviation can indicate fouling or another operational issue, but it does not by itself prove biofouling."
)

# -----------------------------
# Inputs
# -----------------------------
st.subheader("1) Operating conditions")

c1, c2 = st.columns(2)

with c1:
    feed_flow = st.number_input(
        "Feed flowrate (L/min)",
        min_value=float(ranges["Feed Flowrate (L/min)"]["min"]),
        max_value=float(ranges["Feed Flowrate (L/min)"]["max"]),
        value=float(ranges["Feed Flowrate (L/min)"]["median"]),
        step=0.01,
    )

    feed_pressure = st.number_input(
        "Feed pressure (psi)",
        min_value=float(ranges["Feed Pressure (psi)"]["min"]),
        max_value=float(ranges["Feed Pressure (psi)"]["max"]),
        value=float(ranges["Feed Pressure (psi)"]["median"]),
        step=1.0,
    )

with c2:
    feed_cond = st.number_input(
        "Feed conductivity (mS/cm)",
        min_value=float(ranges["Feed Conductivity (mS/cm)"]["min"]),
        max_value=float(ranges["Feed Conductivity (mS/cm)"]["max"]),
        value=float(ranges["Feed Conductivity (mS/cm)"]["median"]),
        step=0.01,
    )

    feed_temp = st.number_input(
        "Feed temperature (°C)",
        min_value=float(ranges["Feed Temperature (C)"]["min"]),
        max_value=float(ranges["Feed Temperature (C)"]["max"]),
        value=float(ranges["Feed Temperature (C)"]["median"]),
        step=0.01,
    )

st.subheader("2) Observed membrane performance")

actual_flux = st.number_input(
    "Actual observed water flux (LMH)",
    min_value=0.0,
    value=0.0,
    step=0.1,
    help="Enter the measured water flux from the RO system. Leave 0 if you only want the expected baseline."
)

row = pd.DataFrame([{
    "Feed Flowrate (L/min)": feed_flow,
    "Feed Pressure (psi)": feed_pressure,
    "Feed Conductivity (mS/cm)": feed_cond,
    "Feed Temperature (C)": feed_temp,
}])

st.divider()

if st.button("Analyze membrane", type="primary", use_container_width=True):
    predicted = float(model.predict(row)[0])

    # Top summary cards
    st.subheader("3) Membrane performance summary")
    m1, m2, m3 = st.columns(3)

    with m1:
        st.metric("Expected water flux", f"{predicted:.2f} LMH")

    if actual_flux > 0:
        deviation_pct = (actual_flux - predicted) / predicted * 100.0

        with m2:
            st.metric(
                "Actual water flux",
                f"{actual_flux:.2f} LMH",
                delta=f"{deviation_pct:+.1f}% vs expected"
            )

        # Status thresholds
        if deviation_pct >= -5:
            status = "Normal"
            status_text = "Performance is close to the expected steady-state baseline."
            status_box = "success"
        elif deviation_pct >= -10:
            status = "Monitor"
            status_text = "Moderate performance deviation. Continue monitoring and inspect operating conditions."
            status_box = "warning"
        else:
            status = "Investigate"
            status_text = "Large performance deviation. Inspection is recommended."
            status_box = "error"

        with m3:
            st.metric("Membrane status", status)

        if status_box == "success":
            st.success(status_text)
        elif status_box == "warning":
            st.warning(status_text)
        else:
            st.error(status_text)

        # Comparison chart
        chart_df = pd.DataFrame({
            "Flux type": ["Expected", "Actual"],
            "Water flux (LMH)": [predicted, actual_flux]
        }).set_index("Flux type")

        st.subheader("4) Expected vs actual")
        st.bar_chart(chart_df)

        # Decision-support interpretation
        st.subheader("5) Decision support")
        if deviation_pct >= -5:
            st.write("**Recommended action:** Continue normal monitoring.")
        elif deviation_pct >= -10:
            st.write("**Recommended action:** Re-check operating conditions and monitor the trend closely.")
        else:
            st.write("**Recommended action:** Investigate the membrane and process conditions. Cleaning or inspection may be needed depending on the root cause.")

        st.caption(
            "Important: Lower-than-expected flux may result from fouling, scaling, temperature effects, "
            "feed changes, hydraulic conditions, or sensor/operational issues. This prototype does not identify the root cause."
        )

    else:
        with m2:
            st.metric("Actual water flux", "Not entered")
        with m3:
            st.metric("Membrane status", "Baseline only")

        st.info(
            "Enter an actual observed flux to compare real membrane performance against the model baseline."
        )

    # About / technical section
    with st.expander("About AquaShield Predict v2"):
        st.write(
            "**Current function:** predicts expected RO water flux from feed flowrate, feed pressure, "
            "feed conductivity, and feed temperature."
        )
        st.write(
            f"**Model test R²:** {meta['metrics']['test_r2']:.3f}"
        )
        st.write(
            f"**Mean absolute error:** {meta['metrics']['test_mae_lmh']:.2f} LMH"
        )
        st.write(
            "**Current limitation:** this is a performance-monitoring prototype, not yet a direct biofouling predictor."
        )
        st.write(
            "**Future direction:** combine operating data with biofouling-specific measurements and AquaShield coating experiments "
            "to build a more complete membrane digital twin."
        )
