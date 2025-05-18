import streamlit as st
import pandas as pd
from datetime import datetime
from utils import (
    load_data_from_sheet,
    add_data,
    merge_start_stop,
    save_merged_data_to_sheet,
    sheet,
    validate_inputs,
    spreadsheet,
    display_and_merge_data,
    require_roles
)
from constants import MERGED_SHEET

# --- Page Config ---
st.set_page_config(page_title="Data Entry", page_icon="📋")

st.markdown(
    """
    <div style='text-align: center;'>
        <h2>📋 Field Monitoring Data Entry</h2>
        <p style='color: grey;'>Use this page to input daily observations, instrument readings, and site information.</p>
    </div>
    <hr>
    """,
    unsafe_allow_html=True
)

require_roles("admin", "editor", "collector")

# --- Dropdown Options ---
ids = ["", '1', '2', '3', '4', '5', '6', '7', '8', '9', '10']
sites = ["", 'Kaneshie First Light', 'Tetteh Quarshie', 'Achimota', 'La',
         'Mallam Market', 'Graphic Road', 'Weija', 'Tantra Hill', 'Amasaman']
officers = ['Obed', 'Clement', 'Peter', 'Ben', 'Mawuli']
wind_directions = ["", "N", "NE", "E", "SE", "S", "SW", "W", "NW"]
weather_conditions = ["", "Sunny", "Cloudy", "Partly Cloudy", "Rainy", "Windy", "Hazy", "Stormy", "Foggy"]

id_to_site = dict(zip(ids, sites))

# --- Entry Type Selection ---
entry_type = st.selectbox("📝 Select Entry Type", ["", "START", "STOP"])

if entry_type:
    # Place ID selection outside the form so the site updates dynamically
    id_selected = st.selectbox("📌 Select Site ID", ids)
    site_selected = id_to_site.get(id_selected, "")

    with st.form("setup_form"):
        site_display = st.text_input("🛰️ Site", value=site_selected, disabled=True)
        officer_selected = st.multiselect("🧑‍🔬 Monitoring Officer(s)", officers)
        driver_name = st.text_input("🧑‍🌾 Driver's Name")

        proceed = st.form_submit_button("➡️ Proceed")

    if proceed and all([id_selected, site_selected, officer_selected, driver_name]):
        st.session_state.entry_ready = True
        st.session_state.entry_type = entry_type
        st.session_state.id_selected = id_selected
        st.session_state.site_selected = site_selected
        st.session_state.officer_selected = officer_selected
        st.session_state.driver_name = driver_name
    elif proceed:
        st.error("⚠ Please complete all required fields to proceed.")

# --- START SECTION ---
if st.session_state.get("entry_ready") and st.session_state.get("entry_type") == "START":
    with st.expander("🟢 Start Day Monitoring", expanded=True):
        start_date = st.date_input("📆 Start Date", value=datetime.today())
        start_time = st.time_input("⏱️ Start Time", value=datetime.now().time())
        start_obs = st.text_area("🧿 First Day Observation")

        st.markdown("#### 🌧️ Initial Atmospheric Conditions")
        start_temp = st.number_input("🌡️ Temperature (°C)", step=0.1)
        start_rh = st.number_input("🌬️ Relative Humidity (%)", step=0.1)
        start_pressure = st.number_input("🧭 Pressure (mbar)", step=0.1)
        start_weather = st.selectbox("🌦️ Weather", weather_conditions)
        start_wind_speed = st.text_input("💨 Wind Speed (e.g. 10 km/h)")
        start_wind_direction = st.selectbox("🌪️ Wind Direction", wind_directions)

        st.markdown("#### ⚙ Initial Sampler Information")
        start_elapsed = st.number_input("⏰ Initial Elapsed Time (min)", step=1)
        start_flow = st.number_input("🧯 Initial Flow Rate (L/min)", step=0.1)

        if st.button("✅ Submit Start Day Data"):
            if validate_inputs(start_temp, start_rh, start_pressure, start_wind_speed):
                start_row = [
                    "START",
                    st.session_state.id_selected,
                    st.session_state.site_selected,
                    ", ".join(st.session_state.officer_selected),
                    st.session_state.driver_name,
                    start_date.strftime("%Y-%m-%d"),
                    start_time.strftime("%H:%M:%S"),
                    start_temp,
                    start_rh,
                    start_pressure,
                    start_weather,
                    start_wind_speed,
                    start_wind_direction,
                    start_elapsed,
                    start_flow,
                    start_obs
                ]
                add_data(start_row)
                st.success("✅ Start day data submitted successfully!")

# --- STOP SECTION ---
elif st.session_state.get("entry_ready") and st.session_state.get("entry_type") == "STOP":
    with st.expander("🔴 Stop Day Monitoring", expanded=True):
        stop_date = st.date_input("📆 Stop Date", value=datetime.today())
        stop_time = st.time_input("⏱️ Stop Time", value=datetime.now().time())
        stop_obs = st.text_area("🧿 Final Day Observation")

        st.markdown("#### 🌧️ Final Atmospheric Conditions")
        stop_temp = st.number_input("🌡️ Final Temperature (°C)", step=0.1)
        stop_rh = st.number_input("🌬️ Final Relative Humidity (%)", step=0.1)
        stop_pressure = st.number_input("🧭 Final Pressure (mbar)", step=0.1)
        stop_weather = st.selectbox("🌦️ Final Weather", weather_conditions)
        stop_wind_speed = st.text_input("💨 Final Wind Speed (e.g. 12 km/h)")
        stop_wind_direction = st.selectbox("🌪️ Final Wind Direction", wind_directions)

        st.markdown("#### ⚙ Final Sampler Information")
        stop_elapsed = st.number_input("⏰ Final Elapsed Time (min)", step=1)
        stop_flow = st.number_input("🧯 Final Flow Rate (L/min)", step=0.1)

        if st.button("✅ Submit Stop Day Data"):
            if validate_inputs(stop_temp, stop_rh, stop_pressure, stop_wind_speed):
                stop_row = [
                    "STOP",
                    st.session_state.id_selected,
                    st.session_state.site_selected,
                    ", ".join(st.session_state.officer_selected),
                    st.session_state.driver_name,
                    stop_date.strftime("%Y-%m-%d"),
                    stop_time.strftime("%H:%M:%S"),
                    stop_temp,
                    stop_rh,
                    stop_pressure,
                    stop_weather,
                    stop_wind_speed,
                    stop_wind_direction,
                    stop_elapsed,
                    stop_flow,
                    stop_obs
                ]
                add_data(stop_row)
                st.success("✅ Stop day data submitted successfully!")

# --- Footer ---
st.markdown("""
    <hr style="margin-top: 40px; margin-bottom:10px">
    <div style='text-align: center; color: grey; font-size: 0.9em;'>
        © 2025 EPA Ghana · Developed by Clement Mensah Ackaah · Built with ❤️ using Streamlit
    </div>
""", unsafe_allow_html=True)
