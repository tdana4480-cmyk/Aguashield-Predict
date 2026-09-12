
import streamlit as st
import pandas as pd
import joblib
import json
from pathlib import Path

st.set_page_config(
    page_title="AquaShield Predict",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded"
)

BASE = Path(__file__).parent
model = joblib.load(BASE / "model.pkl")
meta = json.loads((BASE / "metadata.json").read_text(encoding="utf-8"))
ranges = meta["ranges"]

# -----------------------------
# Styling
# -----------------------------
st.markdown("""
<style>
.block-container {padding-top: 1.4rem; padding-bottom: 2rem;}
[data-testid="stSidebar"] {background: linear-gradient(180deg,#f4fbff 0%,#eef6ff 100%);}
.hero {
    padding: 2rem;
    border-radius: 24px;
    background: linear-gradient(135deg,#eef8ff 0%,#f8fbff 55%,#eefcf7 100%);
    border: 1px solid #d7e8f7;
    margin-bottom: 1rem;
}
.hero h1 {font-size: 3rem; margin-bottom: 0.25rem;}
.hero p {font-size: 1.1rem; color:#35506b;}
.badge {
    display:inline-block; padding:0.35rem 0.7rem; border-radius:999px;
    background:#e8f4ff; color:#0b5fa5; font-weight:600; margin-right:0.4rem;
}
.membrane-card {
    border:1px solid #dce7f1; border-radius:20px; padding:1.2rem;
    min-height:210px; background:white;
}
.status-ok {color:#0f8a4b; font-weight:700;}
.status-soon {color:#8a6a00; font-weight:700;}
.small-muted {color:#6d7f90; font-size:0.95rem;}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# Sidebar navigation
# -----------------------------
st.sidebar.markdown("## 💧 AquaShield")
st.sidebar.caption("Protect • Predict • Evolve")
page = st.sidebar.radio(
    "Navigate",
    ["Home", "Membrane Explorer", "AI Analysis", "About"],
    index=0
)

# -----------------------------
# HOME
# -----------------------------
if page == "Home":
    st.markdown("""
    <div class="hero">
      <span class="badge">Miyahthon 3</span>
      <span class="badge">Water Reuse</span>
      <h1>AquaShield <span style="color:#2f7de1;">Predict</span></h1>
      <p><b>AI-assisted membrane performance monitoring</b></p>
      <p>
        AquaShield combines a future anti-biofouling membrane surface strategy with
        intelligent performance monitoring for membrane systems.
      </p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("### 🛡️ Protect")
        st.write("Future surface modification concept designed to reduce microbial attachment and biofilm formation.")
    with c2:
        st.markdown("### 🧠 Predict")
        st.write("AI-assisted monitoring compares expected membrane performance with observed performance.")
    with c3:
        st.markdown("### 🔄 Evolve")
        st.write("Long-term direction: combine operating data, biofouling measurements, and sensor data into a fuller digital twin.")

    st.divider()
    st.subheader("Project flow")
    st.write("**1. Select a membrane → 2. Explore its structure → 3. Run AI analysis when a trained model is available → 4. Review performance status and recommendations.**")

    st.info("Current AI model availability: **RO only**. NF and UF are available for exploration, but their AI models are not yet trained.")

# -----------------------------
# MEMBRANE EXPLORER
# -----------------------------
elif page == "Membrane Explorer":
    st.title("🧬 Membrane Explorer")
    st.caption("Explore common membrane types and see which are currently supported by AquaShield Predict.")

    membrane = st.radio(
        "Select membrane type",
        ["RO — Reverse Osmosis", "NF — Nanofiltration", "UF — Ultrafiltration"],
        horizontal=True
    )

    if membrane.startswith("RO"):
        st.success("AI Prediction Available ✅")
        a, b = st.columns([1.2, 1])
        with a:
            st.markdown("### RO membrane")
            st.write(
                "Reverse osmosis membranes are dense selective membranes commonly used for desalination and high-rejection water treatment."
            )
            st.markdown("""
            **AquaShield status**
            - AI monitoring model: **Available**
            - Current model target: **Expected water flux**
            - Current inputs: feed flowrate, pressure, conductivity, temperature
            - Biofouling-specific diagnosis: **Not yet available**
            """)
        with b:
            st.markdown("### Simplified structure")
            st.code(
"""Feed water
   ↓
[ Feed spacer ]
[ Polyamide active layer ]
[ Support layer ]
[ Permeate carrier ]
   ↓
Permeate (cleaner water)
Concentrate → rejected salts/solutes""",
                language="text"
            )

    elif membrane.startswith("NF"):
        st.warning("Explore only — AI model coming later ⏳")
        st.markdown("### NF membrane")
        st.write(
            "Nanofiltration sits between RO and UF in selectivity. It is often used for partial salt rejection, hardness removal, and organic matter control."
        )
        st.markdown("""
        **AquaShield status**
        - Membrane explorer: **Available**
        - AI prediction: **Not available yet**
        - Required next step: obtain a suitable NF dataset and train a dedicated NF model
        """)
        st.code(
"""Feed water
   ↓
[ NF selective layer ]
[ Porous support ]
   ↓
Permeate
Concentrate""",
            language="text"
        )

    else:
        st.warning("Explore only — AI model coming later ⏳")
        st.markdown("### UF membrane")
        st.write(
            "Ultrafiltration is a porous membrane process commonly used to remove suspended solids, colloids, and larger biological material."
        )
        st.markdown("""
        **AquaShield status**
        - Membrane explorer: **Available**
        - AI prediction: **Not available yet**
        - Required next step: obtain a suitable UF dataset and train a dedicated UF model
        """)
        st.code(
"""Feed water
   ↓
[ Porous UF membrane ]
   ↓
Permeate
Retained particles / macromolecules""",
            language="text"
        )

    st.info("Why separate models? RO, NF, and UF operate differently, so one RO-trained model should not be used to make predictions for NF or UF.")

# -----------------------------
# AI ANALYSIS
# -----------------------------
elif page == "AI Analysis":
    st.title("🤖 AquaShield Predict — RO Analysis")
    st.caption("Current trained model: Reverse Osmosis (RO)")

    st.info(
        "This model predicts expected RO water flux from operating conditions, then compares it with observed flux. "
        "A performance deviation may indicate fouling or another operational issue, but it does not by itself prove biofouling."
    )

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

    if st.button("Analyze membrane", type="primary", use_container_width=True):
        predicted = float(model.predict(row)[0])

        st.subheader("3) Membrane performance summary")
        m1, m2, m3 = st.columns(3)
        with m1:
            st.metric("Expected water flux", f"{predicted:.2f} LMH")

        if actual_flux > 0:
            deviation_pct = (actual_flux - predicted) / predicted * 100.0

            if deviation_pct >= -5:
                status = "Normal"
                status_text = "Performance is close to the expected baseline."
                box = "success"
            elif deviation_pct >= -10:
                status = "Monitor"
                status_text = "Moderate performance deviation. Continue monitoring and inspect operating conditions."
                box = "warning"
            else:
                status = "Investigate"
                status_text = "Large performance deviation. Inspection is recommended."
                box = "error"

            with m2:
                st.metric("Actual water flux", f"{actual_flux:.2f} LMH", delta=f"{deviation_pct:+.1f}% vs expected")
            with m3:
                st.metric("Membrane status", status)

            if box == "success":
                st.success(status_text)
            elif box == "warning":
                st.warning(status_text)
            else:
                st.error(status_text)

            chart_df = pd.DataFrame({
                "Flux type": ["Expected", "Actual"],
                "Water flux (LMH)": [predicted, actual_flux]
            }).set_index("Flux type")

            st.subheader("4) Expected vs actual")
            st.bar_chart(chart_df)

            st.subheader("5) Decision support")
            if deviation_pct >= -5:
                st.write("**Recommended action:** Continue normal monitoring.")
            elif deviation_pct >= -10:
                st.write("**Recommended action:** Re-check operating conditions and monitor the trend closely.")
            else:
                st.write("**Recommended action:** Investigate the membrane and process conditions. Cleaning or inspection may be needed depending on the root cause.")

            st.caption(
                "Lower-than-expected flux may result from fouling, scaling, feed changes, temperature effects, "
                "hydraulic conditions, or sensor/operational issues."
            )
        else:
            with m2:
                st.metric("Actual water flux", "Not entered")
            with m3:
                st.metric("Membrane status", "Baseline only")
            st.info("Enter an actual observed flux to compare real membrane performance against the AI baseline.")

        with st.expander("Model details"):
            st.write(f"**Model test R²:** {meta['metrics']['test_r2']:.3f}")
            st.write(f"**Mean absolute error:** {meta['metrics']['test_mae_lmh']:.2f} LMH")
            st.write("**Current target:** expected water flux")
            st.write("**Current membrane type:** RO only")
            st.write("**Current limitation:** not yet a direct biofouling classifier.")

# -----------------------------
# ABOUT
# -----------------------------
else:
    st.title("ℹ️ About AquaShield")
    st.markdown("""
    **AquaShield** is being developed as a membrane-focused concept with two complementary directions:

    **Protect** — a future surface-modification strategy intended to reduce microbial attachment and biofilm formation.

    **Predict** — an AI-assisted membrane performance monitoring system that compares expected and observed performance.

    The current software prototype is trained on **RO membrane operating data** and predicts **expected water flux**.
    It does not yet directly diagnose biofouling.

    **Future development**
    - Add biofouling-specific measurements
    - Add coating-performance data
    - Add dedicated NF and UF models
    - Add interactive 3D membrane visualization
    - Build toward a fuller membrane digital twin
    """)
