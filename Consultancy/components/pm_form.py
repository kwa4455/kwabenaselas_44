import streamlit as st
from datetime import datetime
from resource import (
    load_data_from_sheet,
    add_data,
    merge_start_stop,
    save_merged_data_to_sheet,
    sheet,
    spreadsheet,
    display_and_merge_data
)
from constants import MERGED_SHEET
from modules.authentication import require_role
from general import sector_data  # Assumes your sector_data is saved here

# -----------------------------
# Constants and configuration
# -----------------------------
officers = ['Obed Korankye', 'Clement Ackaah', 'Peter Ohene-Twum', 'Benjamin Essien', 'Mawuli Amegah']
wind_directions = ["-- Select --", "N", "NE", "E", "SE", "S", "NNE", "NEN", "SWS", "SES", "SSW", "SW", "W", "NW"]
weather_conditions = ["-- Select --", "Sunny", "Cloudy", "Partly Cloudy", "Rainy", "Windy", "Hazy", "Stormy", "Foggy"]
sampling_points = ["-- Select --", "Point 1", "Point 2", "Point 3", "Point 4"]
pollutants = ["-- Select --", "PM₂.₅", "PM₁₀", "TSP"]
drivers = ["Kanazoe Sia", "Kofi Adjei", "Fatau"]

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

def get_companies(sector):
    return list(sector_data.get(sector, {}).get("companies", {}).keys())

def get_region_city(company_name):
    for sector in sector_data.values():
        companies = sector.get("companies", {})
        if company_name in companies:
            info = companies[company_name]
            return info.get("region", "Unknown"), info.get("city", "Unknown")
    return "Unknown", "Unknown"

def get_custom_time(label, key_prefix, hour_key="hour", minute_key="minute"):
    col1, col2 = st.columns(2)
    with col1:
        hour = st.selectbox(f"{label} - Hour", list(range(0, 24)), key=f"{key_prefix}_{hour_key}")
    with col2:
        minute = st.selectbox(f"{label} - Minute", list(range(0, 60)), key=f"{key_prefix}_{minute_key}")
    return datetime.strptime(f"{hour}:{minute}", "%H:%M").time()

def show():
    require_role(["admin", "officer"])
    st.title("📝 Field Observation Entry")

    entry_type = st.selectbox("Select Entry Type", ["", "START", "STOP"])
    if not entry_type:
        return

    # Sector and Company
    sector_options = ["-- Select --"] + list(sector_data.keys())
    selected_sector = st.selectbox("🏭 Select Industry Sector", sector_options)
    if selected_sector == "-- Select --":
        return

    company_options = ["-- Select --"] + get_companies(selected_sector)
    selected_company = st.selectbox("🏢 Select Company", company_options)
    if selected_company == "-- Select --":
        return

    region, city = get_region_city(selected_company)
    st.text_input("🌍 Region", value=region, disabled=True)
    st.text_input("🏙️ Town/City", value=city, disabled=True)
    
    st.subheader("5. Officer(s) Involved")
    officer_selected = st.multiselect("👷 Monitoring Officer(s)", officers)
    driver = st.selectbox("🧑‍🌾 Select Driver", ["-- Select --"] + drivers, key="driver")

    wind_speed_options = [f"{x:.1f}" for x in [i * 0.5 for i in range(0, 41)]]

    # ------------------ START ENTRY ------------------
    if entry_type == "START":
        st.subheader("🟢 Start Monitoring")

        start_sampling_point = st.selectbox("📍 Sampling Point", sampling_points)
        sampling_point_description = st.text_input("📍 Sampling Point Description")
        longitude = st.number_input("🌐 Longitude", step=0.0001, format="%.4f")
        latitude = st.number_input("🌐 Latitude", step=0.0001, format="%.4f")
        pollutants_selected = st.multiselect("🌫️ Pollutant", pollutants)

        st.subheader("3. Date and Time")
        start_date = st.date_input("📅 Start Date", value=datetime.today())
        start_time = get_custom_time("⏱️ Start Time", "start")
        start_date_time = datetime.combine(start_date, start_time)

        start_obs = st.text_area("🧿 Final Observations")

        start_weather = st.selectbox("🌦️ Weather", weather_conditions)
        if start_weather != "-- Select --":
            temp_options = ["-- Select --"] + weather_defaults[start_weather]["temp"]
            rh_options = ["-- Select --"] + weather_defaults[start_weather]["rh"]
            start_temp = st.selectbox("🌡️ Temperature (°C)", temp_options)
            start_rh = st.selectbox("💧 Humidity (%)", rh_options)
        else:
            start_temp = start_rh = "-- Select --"

        start_pressure = st.number_input("🧭 Pressure (mbar)", step=0.1)
        start_wind_speed = st.selectbox("💨 Wind Speed (km/h)", ["-- Select --"] + wind_speed_options)
        start_wind_speed = float(start_wind_speed) if start_wind_speed != "-- Select --" else None
        start_wind_direction = st.selectbox("🌪️ Wind Direction", wind_directions)

        start_elapsed = st.number_input("⏰ Elapsed Time (min)", step=0.1)
        start_flow = st.selectbox("🧯 Flow Rate (L/min)", options=[5, 16.7])

        if st.button("✅ Submit Start Day Data"):
            if not all([selected_sector, selected_company, region, city, officer_selected, driver_name]):
                st.error("⚠ Please complete all required fields before submitting.")
                return
            if start_weather == "-- Select --" or start_temp == "-- Select --" or start_rh == "-- Select --" or start_wind_direction == "-- Select --" or start_wind_speed is None:
                st.error("⚠ Please select valid weather, temperature, humidity, wind direction, and wind speed.")
                return

            start_row = [
                "START", selected_sector, selected_company, region, city,
                start_sampling_point, sampling_point_description, longitude, latitude,
                ", ".join(pollutants_selected), ", ".join(officer_selected), driver_name,
                start_date_time.strftime("%Y-%m-%d %H:%M:%S"),
                start_temp, start_rh, start_pressure, start_weather,
                start_wind_speed, start_wind_direction,
                start_elapsed, start_flow, start_obs
            ]
            add_data(start_row, st.session_state.username)
            st.success("✅ Start day data submitted successfully!")

    # ------------------ STOP ENTRY ------------------
    elif entry_type == "STOP":
        st.subheader("🔴 Stop Monitoring")

        stop_sampling_point = st.selectbox("📍 Sampling Point", sampling_points)
        stop_date = st.date_input("📅 Stop Date", value=datetime.today())
        stop_time = get_custom_time("⏱️ Stop Time", "stop")
        stop_date_time = datetime.combine(stop_date, stop_time)

        stop_obs = st.text_area("🧿 Final Observations")

        stop_weather = st.selectbox("🌦️ Final Weather", weather_conditions)
        if stop_weather != "-- Select --":
            temp_options = ["-- Select --"] + weather_defaults[stop_weather]["temp"]
            rh_options = ["-- Select --"] + weather_defaults[stop_weather]["rh"]
            stop_temp = st.selectbox("🌡️ Final Temperature (°C)", temp_options)
            stop_rh = st.selectbox("💧 Final Humidity (%)", rh_options)
        else:
            stop_temp = stop_rh = "-- Select --"

        stop_pressure = st.number_input("🧭 Final Pressure (mbar)", step=0.1)
        stop_wind_speed = st.selectbox("💨 Final Wind Speed (km/h)", ["-- Select --"] + wind_speed_options)
        stop_wind_speed = float(stop_wind_speed) if stop_wind_speed != "-- Select --" else None
        stop_wind_direction = st.selectbox("🌪️ Final Wind Direction", wind_directions)

        stop_elapsed = st.number_input("⏰ Final Elapsed Time (min)", step=0.1)
        stop_flow = st.selectbox("🧯 Final Flow Rate (L/min)", options=[5, 16.7])

        if st.button("✅ Submit Stop Day Data"):
            if not all([selected_sector, selected_company, officer_selected, driver_name]):
                st.error("⚠ Please complete all required fields before submitting.")
                return
            if stop_weather == "-- Select --" or stop_temp == "-- Select --" or stop_rh == "-- Select --" or stop_wind_direction == "-- Select --" or stop_wind_speed is None:
                st.error("⚠ Please select valid weather, temperature, humidity, wind direction, and wind speed.")
                return

            stop_row = [
                "STOP", selected_sector, selected_company, region, city,
                stop_sampling_point, "", "", "",  # No GPS or description
                "", ", ".join(officer_selected), driver_name,
                stop_date_time.strftime("%Y-%m-%d %H:%M:%S"),
                stop_temp, stop_rh, stop_pressure, stop_weather,
                stop_wind_speed, stop_wind_direction,
                stop_elapsed, stop_flow, stop_obs
            ]
            add_data(stop_row, st.session_state.username)
            st.success("✅ Stop day data submitted successfully!")

 
