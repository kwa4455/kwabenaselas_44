import streamlit as st
from datetime import datetime, time
import pandas as pd
import os

from modules.authentication import require_role
from general import sector_data  # Assumes your sector_data is saved here


def show():
    require_role(["admin", "officer"])

officers = ['Obed Korankye', 'Clement Ackaah', 'Peter Ohene-Twum', 'Benjamin Essien', 'Mawuli Amegah']
wind_directions = ["-- Select --", "N", "NE", "E", "SE", "S","NNE", "NEN","SWS", "SES", "SSW","SW", "W", "NW"]
weather_conditions = ["-- Select --", "Sunny", "Cloudy", "Partly Cloudy", "Rainy", "Windy", "Hazy", "Stormy", "Foggy"]
sampling_points = ["-- Select --", "Point 1", "Point 2", "Point 3", "Point 4"]
pollutants = ["-- Select --",  "PM₂.₅", "PM₁₀", "TSP"]

weather_defaults = {
    "Sunny": {"temp": list(range(25, 41)), "rh": list(range(40, 91))},
    "Rainy": {"temp": list(range(20, 27)), "rh": list(range(70, 101))},
    "Cloudy": {"temp": list(range(25, 35)), "rh": list(range(40, 91))},
    "Partly Cloudy": {"temp": list(range(21, 35)), "rh": list(range(35, 91))},
    "Windy": {"temp": list(range(20, 30)), "rh": list(range(40, 91))},
    "Hazy": {"temp": list(range(20, 31)), "rh": list(range(40, 91))},
    "Stormy": {"temp": list(range(17, 25)), "rh": list(range(80, 101))},
    "Foggy": {"temp": list(range(15, 22)), "rh": list(range(85, 101))}
}

# --- Helper Functions ---
def get_companies(sector):
    return list(sector_data.get(sector, {}).get("companies", {}).keys())

def get_region_city(company_name):
    for sector in sector_data.values():
        companies = sector.get("companies", {})
        if company_name in companies:
            info = companies[company_name]
            return info.get("region", "Unknown"), info.get("city", "Unknown")
    return "Unknown", "Unknown"

def get_custom_time(label_prefix, key_prefix, hour_key, minute_key):
    hour = st.selectbox(f"{label_prefix} Hour", list(range(0, 24)), key=f"{key_prefix}_{hour_key}")
    valid_minutes = [m for m in range(60) if m not in [0, 15, 30, 45]]
    minute = st.selectbox(f"{label_prefix} Minute (not 00, 15, 30, 45)", valid_minutes, key=f"{key_prefix}_{minute_key}")
    return time(hour=hour, minute=minute)



# --- UI ---
st.title("📝 Monitoring Data Entry")
entry_type = st.selectbox("Select Entry Type", ["", "START", "STOP"])

selected_sector = selected_company = region = city = ""

if entry_type:
    sector_options = ["-- Select --"] + list(sector_data.keys())
    selected_sector = st.selectbox("🏭 Select Industry Sector", sector_options)

    if selected_sector != "-- Select --":
        company_options = ["-- Select --"] + get_companies(selected_sector)
        selected_company = st.selectbox("🏢 Select Company", company_options)

        if selected_company != "-- Select --":
            region, city = get_region_city(selected_company)
            st.text_input("🌍 Region", value=region, disabled=True)
            st.text_input("🏙️ Town/City", value=city, disabled=True)

    officer_selected = st.multiselect("👷 Monitoring Officer(s)", officers)
    driver_name = st.text_input("🧑‍🌾 Driver's Name")

    # START ENTRY
    if entry_type == "START":
        st.subheader("🟢 Start Monitoring")
        select_sampling_point = st.selectbox("📍 Sampling Point", sampling_points)
        sampling_point_description = st.text_input("📍 Sampling Point Description")
        longitude = st.number_input("🌐 Longitude", step=0.0001, format="%.4f")
        latitude = st.number_input("🌐 Latitude", step=0.0001, format="%.4f")
        pollutants_selected = st.multiselect("🌫️ Pollutant", pollutants)

        start_date = st.date_input("📅 Start Date", value=datetime.today())
        start_time = get_custom_time("⏱️ Start Time", "start", "hour", "minute")
        start_obs = st.text_area("🧿 Initial Observations")

        start_weather = st.selectbox("🌦️ Weather", weather_conditions)
        if start_weather != "-- Select --":
            temp_options = ["-- Select --"] + weather_defaults.get(start_weather, {}).get("temp", [])
            rh_options = ["-- Select --"] + weather_defaults.get(start_weather, {}).get("rh", [])
            start_temp = st.selectbox("🌡️ Temperature (°C)", temp_options)
            start_rh = st.selectbox("💧 Humidity (%)", rh_options)
        else:
            start_temp = start_rh = "-- Select --"

        start_pressure = st.number_input("🧭 Pressure (mbar)", step=0.1)
        start_wind_speed = st.text_input("💨 Wind Speed")
        start_wind_direction = st.selectbox("🌪️ Wind Direction", wind_directions)

        start_elapsed = st.number_input("⏰ Elapsed Time (min)", step=0.1)
        start_flow = st.selectbox("🧯 Flow Rate (L/min)", options=[5, 16.7])

        
        if st.button("✅ Submit Start Day Data"):
                if not all([selected_sector, selected_company, region, city, officer_selected, driver_name]):
                    st.error("⚠ Please complete all required fields before submitting.")
                    return
                if start_weather == "-- Select --" or start_temp == "-- Select --" or start_rh == "-- Select --" or start_wind_direction == "-- Select --":
                    st.error("⚠ Please select valid weather, temp, RH, and wind direction.")
                    return

                start_row = [
                    "START", selected_sector, selected_company, region, city, start_sampling_point,sampling_point_description, longitude,latitude, pollutants_selected, ", ".join(officer_selected), driver_name,
                    start_date.strftime("%Y-%m-%d"), start_time.strftime("%H:%M:%S"),
                    start_temp, start_rh, start_pressure, start_weather,
                    start_wind_speed, start_wind_direction,
                    start_elapsed, start_flow, start_obs
                ]
                add_data(start_row, st.session_state.username)
                st.success("✅ Start day data submitted successfully!")
    # STOP ENTRY
    elif entry_type == "STOP":
        st.subheader("🔴 Stop Monitoring")
        select_sampling_point = st.selectbox("📍 Sampling Point", sampling_points)
        stop_date = st.date_input("📅 Stop Date", value=datetime.today())
        stop_time = get_custom_time("⏱️ Stop Time", "stop", "hour", "minute")
        stop_obs = st.text_area("🧿 Final Observations")

        stop_weather = st.selectbox("🌦️ Final Weather", weather_conditions)
        if stop_weather != "-- Select --":
            temp_options = ["-- Select --"] + weather_defaults.get(stop_weather, {}).get("temp", [])
            rh_options = ["-- Select --"] + weather_defaults.get(stop_weather, {}).get("rh", [])
            stop_temp = st.selectbox("🌡️ Final Temperature (°C)", temp_options)
            stop_rh = st.selectbox("💧 Final Humidity (%)", rh_options)
        else:
            stop_temp = stop_rh = "-- Select --"

        stop_pressure = st.number_input("🧭 Final Pressure (mbar)", step=0.1)
        stop_wind_speed = st.text_input("💨 Final Wind Speed")
        stop_wind_direction = st.selectbox("🌪️ Final Wind Direction", wind_directions)

        stop_elapsed = st.number_input("⏰ Final Elapsed Time (min)", step=0.1)
        stop_flow = st.selectbox("🧯 Final Flow Rate (L/min)", options=[5, 16.7])
        
        if st.button("✅ Submit Stop Day Data"):
                if not all([id_selected, site_selected, officer_selected, driver_name]):
                    st.error("⚠ Please complete all required fields before submitting.")
                    return
                if stop_weather == "-- Select --" or stop_temp == "-- Select --" or stop_rh == "-- Select --" or stop_wind_direction == "-- Select --":
                    st.error("⚠ Please select valid weather, temp, RH, and wind direction.")
                    return

                stop_row = [
                    "STOP", selected_sector, selected_company,stop_sampling_point ", ".join(officer_selected), driver_name,
                    stop_date.strftime("%Y-%m-%d"), stop_time.strftime("%H:%M:%S"),
                    stop_temp, stop_rh, stop_pressure, stop_weather,
                    stop_wind_speed, stop_wind_direction,
                    stop_elapsed, stop_flow, stop_obs
                ]
                add_data(stop_row, st.session_state.username)
                st.success("✅ Stop day data submitted successfully!"
        

# ----------- Show Data Records -----------
    if st.checkbox("📖 Show Submitted Monitoring Records"):
        try:
            df = load_data_from_sheet(sheet)
            df_saved = display_and_merge_data(df, spreadsheet, MERGED_SHEET)
            st.dataframe(df_saved, use_container_width=True)
        except Exception as e:
            st.warning(f"⚠ Could not load Submitted Monitoring Records: {e}")