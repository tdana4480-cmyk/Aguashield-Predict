
import streamlit as st
import pandas as pd
import joblib
import json
from pathlib import Path

st.set_page_config(page_title="AquaShield Predict", page_icon="💧", layout="centered")

BASE = Path(__file__).parent
model = joblib.load(BASE / "model.pkl")
meta = json.loads((BASE / "metadata.json").read_text(encoding="utf-8"))
ranges = meta["ranges"]

st.title("💧 AquaShield Predict")
st.caption("RO membrane performance prediction — prototype v1")

st.info(
    "This prototype predicts expected water flux from steady-state RO operating conditions. "
    "It is not yet a direct biofouling diagnostic."
)

def slider_for(label, key, step):
    r = ranges[key]
    return st.slider(
        label,
        min_value=float(r["min"]),
        max_value=float(r["max"]),
        value=float(r["median"]),
        step=step,
    )

flow = slider_for("Feed flowrate (L/min)", "Feed Flowrate (L/min)", 0.01)
pressure = slider_for("Feed pressure (psi)", "Feed Pressure (psi)", 1.0)
conductivity = slider_for("Feed conductivity (mS/cm)", "Feed Conductivity (mS/cm)", 0.01)
temperature = slider_for("Feed temperature (°C)", "Feed Temperature (C)", 0.001)

st.divider()
observed = st.number_input(
    "Optional: actual observed water flux (LMH)",
    min_value=0.0,
    value=0.0,
    step=0.1,
    help="Enter 0 if you only want the prediction."
)

row = pd.DataFrame([{
    "Feed Flowrate (L/min)": flow,
    "Feed Pressure (psi)": pressure,
    "Feed Conductivity (mS/cm)": conductivity,
    "Feed Temperature (C)": temperature,
}])

if st.button("Analyze membrane", type="primary", use_container_width=True):
    predicted = float(model.predict(row)[0])

    st.metric("Predicted water flux", f"{predicted:.2f} LMH")

    if observed > 0:
        deviation = (observed - predicted) / predicted * 100
        st.metric("Observed vs. expected", f"{deviation:+.1f}%")

        if deviation >= -5:
            st.success("Performance is close to the expected steady-state baseline.")
        elif deviation >= -10:
            st.warning("Moderate performance deviation. Monitor the membrane and operating conditions.")
        else:
            st.error("Large performance deviation. Investigation is recommended.")

        st.caption(
            "A lower-than-expected flux can be caused by fouling, scaling, temperature effects, "
            "feed changes, or sensor/operational issues. This prototype does not identify the cause."
        )

    with st.expander("About this prototype"):
        st.write(
            "Model inputs: feed flowrate, feed pressure, feed conductivity, and feed temperature. "
            "Target: water flux (LMH)."
        )
        st.write(
            f"Model test R²: {meta['metrics']['test_r2']:.3f} | "
            f"Mean absolute error: {meta['metrics']['test_mae_lmh']:.2f} LMH"
        )
        st.write(
            "AquaShield future direction: combine this predictive baseline with biofouling-specific "
            "data and coating experiments to support a future membrane digital twin."
        )
