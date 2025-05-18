import streamlit as st
from datetime import datetime
from utils import (
    add_data,
    require_roles
)
from constants import MERGED_SHEET

# Config
st.set_page_config(page_title="Data Entry", page_icon="📋")
require_roles("admin", "editor", "collector")

# --- Setup ---
ids = ["", '1', '2', '3', '4', '5', '6', '7', '8', '9', '10']
site_id_map = {
    '1': 'Kaneshie First Light',
    '2': 'Tetteh Quarshie',
    '3': 'Achimota',
    '4': 'La',
    '5': 'Mallam Market',
    '6': 'Graphic Road',
    '7': 'Weija',
    '8': 'Tantra Hill',
    '9': 'Amasaman',
    '10': 'Other'
}
officers = ['Obed', 'Clement', 'Peter', 'Ben', 'Mawuli']
wind_directions = ["", "N", "NE", "E", "SE", "S", "SW", "W", "NW"]
weather_conditions = ["", "Sunny", "Cloudy", "Partly Cloudy", "Rainy", "Windy", "Hazy", "Stormy", "Foggy"]

# --- Header ---
st.markdown("""
<div style='text-align: center;'>
    <h2>📋 Field Monitoring Data Entry</h2>
    <p style='color: grey;'>Fill in and submit daily monitoring data.</p>
</div><hr>
""", unsafe_allow_html=True)

# --- Session state initialization ---
if "proceed" not in st.session_state:
    st.session_state["proceed"] = False

# --- Step 1: Pre-Form Selections ---
with st.form("basic_info_form"):
    entry_type = st.selectbox("📝 Select Entry Type", ["", "START", "STOP"], key="entry_type")
    id_selected = st.selectbox("📌 Select Site ID", ids, key="site_id")
    site_selected = site_id_map.get(id_selected, "")
    st.text_input("📍 Site", value=site_selected, disabled=True)
    officer_selected = st.multiselect("🧑‍🔬 Monitoring Officer(s)", officers, key="officers")
    driver_name = st.text_input("🧑‍🌾 Driver's Name", key="driver_name")

    if st.form_submit_button("➡️ Proceed"):
        if entry_type and id_selected and officer_selected and driver_name:
            st.session_state["proceed"] = True
        else:
            st.error("⚠️ Please complete all fields before proceeding.")

# --- Step 2: Full Form ---
if st.session_state["proceed"]:
    with st.form("monitoring_data_form"):
        st.markdown(f"### {'🟢 START' if entry_type == 'START' else '🔴 STOP'} Monitoring Form")

        # Common fields
        date = st.date_input("📆 Date", value=datetime.today())
        time = st.time_input("⏱️ Time", value=datetime.now().time())
        obs = st.text_area("🧿 Observation")

        st.markdown("#### 🌧️ Atmospheric Conditions")
        temp = st.number_input("🌡️ Temperature (°C)", min_value=-20.0, max_value=60.0, step=0.1)
        rh = st.number_input("🌬️ Relative Humidity (%)", min_value=0.0, max_value=100.0, step=0.1)
        pressure = st.number_input("🧭 Pressure (mbar)", min_value=800.0, max_value=1100.0, step=0.1)
        weather = st.selectbox("🌦️ Weather", weather_conditions)
        wind_speed = st.text_input("💨 Wind Speed (e.g. 10 km/h)")
        wind_dir = st.selectbox("🌪️ Wind Direction", wind_directions)

        st.markdown("#### ⚙ Sampler Information")
        elapsed = st.number_input("⏰ Elapsed Time (min)", min_value=0, max_value=1440, step=1)
        flow = st.number_input("🧯 Flow Rate (L/min)", min_value=0.0, max_value=100.0, step=0.1)

        if st.form_submit_button("✅ Submit Monitoring Data"):
            row = [
                entry_type, id_selected, site_selected,
                ", ".join(officer_selected), driver_name,
                date.strftime("%Y-%m-%d"), time.strftime("%H:%M:%S"),
                temp, rh, pressure, weather, wind_speed, wind_dir,
                elapsed, flow, obs
            ]
            add_data(row)
            st.success(f"✅ {entry_type} day data submitted successfully!")
            st.session_state["proceed"] = False  # reset

# --- Footer ---
st.markdown("""
<hr style="margin-top: 40px; margin-bottom:10px">
<div style='text-align: center; color: grey; font-size: 0.9em;'>
    © 2025 EPA Ghana · Developed by Clement Mensah Ackaah · Built with ❤️ using Streamlit
</div>
""", unsafe_allow_html=True)
