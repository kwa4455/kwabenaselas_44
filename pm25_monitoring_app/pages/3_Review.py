import streamlit as st
import pandas as pd
from datetime import datetime
from utils import (
    load_data_from_sheet,
    add_data,
    merge_start_stop,
    save_merged_data_to_sheet,
    sheet,
    spreadsheet,
    require_roles
)
from constants import MERGED_SHEET

# --- Page Title ---
st.title("📄 Enter PM₂.₅ Monitoring Data")
st.info("Welcome to the data entry form. Please provide monitoring details below.")
require_roles("admin", "editor", "collector")

# --- Dropdown Options ---
ids = ["", '1', '2', '3', '4', '5', '6', '7', '8', '9', '10']
sites = ["", 'Kaneshie First Light', 'Tetteh Quarshie', 'Achimota', 'La',
         'Mallam Market', 'Graphic Road', 'Weija', 'Tantra Hill', 'Amasaman']
officers = ['Obed', 'Clement', 'Peter', 'Ben', 'Mawuli']
wind_directions = ["", "N", "NE", "E", "SE", "S", "SW", "W", "NW"]
weather_conditions = ["", "Sunny", "Cloudy", "Partly Cloudy", "Rainy", "Windy", "Hazy", "Stormy", "Foggy"]

entry_type = st.selectbox("Select Entry Type", ["", "START", "STOP"])

if entry_type:
    id_selected = st.selectbox("Select Site ID", ids)
    site_selected = st.selectbox("Select Site", sites)
    officer_selected = st.multiselect("Monitoring Officer(s)", officers)
    driver_name = st.text_input("Driver's Name")

# === START Section ===
if entry_type == "START":
    with st.expander("🟢 Start Day Monitoring", expanded=True):
        start_date = st.date_input("Start Date", value=datetime.today())
        start_time = st.time_input("Start Time", value=datetime.now().time())
        start_obs = st.text_area("First Day Observation")

        st.markdown("#### 🌡 Initial Atmospheric Conditions")
        start_temp = st.number_input("Temperature (°C)", step=0.1)
        start_rh = st.number_input("Relative Humidity (%)", step=0.1)
        start_pressure = st.number_input("Pressure (mbar)", step=0.1)
        start_weather = st.selectbox("Weather", weather_conditions)
        start_wind_speed = st.text_input("Wind Speed (e.g. 10 km/h)")
        start_wind_direction = st.selectbox("Wind Direction", wind_directions)

        st.markdown("#### ⚙ Initial Sampler Information")
        start_elapsed = st.number_input("Initial Elapsed Time (min)", step=1)
        start_flow = st.number_input("Initial Flow Rate (L/min)", step=0.1)

        if st.button("✅ Submit Start Day Data"):
            if all([id_selected, site_selected, officer_selected, driver_name]):
                start_row = [
                    "START", id_selected, site_selected, ", ".join(officer_selected), driver_name,
                    start_date.strftime("%Y-%m-%d"), start_time.strftime("%H:%M:%S"),
                    start_temp, start_rh, start_pressure, start_weather,
                    start_wind_speed, start_wind_direction,
                    start_elapsed, start_flow, start_obs
                ]
                add_data(start_row)
                st.success("✅ Start day data submitted successfully!")
            else:
                st.error("⚠ Please complete all required fields before submitting.")

# === STOP Section ===
elif entry_type == "STOP":
    with st.expander("🔴 Stop Day Monitoring", expanded=True):
        stop_date = st.date_input("Stop Date", value=datetime.today())
        stop_time = st.time_input("Stop Time", value=datetime.now().time())
        stop_obs = st.text_area("Final Day Observation")

        st.markdown("#### 🌡 Final Atmospheric Conditions")
        stop_temp = st.number_input("Final Temperature (°C)", step=0.1)
        stop_rh = st.number_input("Final Relative Humidity (%)", step=0.1)
        stop_pressure = st.number_input("Final Pressure (mbar)", step=0.1)
        stop_weather = st.selectbox("Final Weather", weather_conditions)
        stop_wind_speed = st.text_input("Final Wind Speed (e.g. 12 km/h)")
        stop_wind_direction = st.selectbox("Final Wind Direction", wind_directions)

        st.markdown("#### ⚙ Final Sampler Information")
        stop_elapsed = st.number_input("Final Elapsed Time (min)", step=1)
        stop_flow = st.number_input("Final Flow Rate (L/min)", step=0.1)

        if st.button("✅ Submit Stop Day Data"):
            if all([id_selected, site_selected, officer_selected, driver_name]):
                stop_row = [
                    "STOP", id_selected, site_selected, ", ".join(officer_selected), driver_name,
                    stop_date.strftime("%Y-%m-%d"), stop_time.strftime("%H:%M:%S"),
                    stop_temp, stop_rh, stop_pressure, stop_weather,
                    stop_wind_speed, stop_wind_direction,
                    stop_elapsed, stop_flow, stop_obs
                ]
                add_data(stop_row)
                st.success("✅ Stop day data submitted successfully!")
            else:
                st.error("⚠ Please complete all required fields before submitting.")

# === Merge START/STOP and show merged records ===
st.markdown("## 🔗 Merge START/STOP Records")

if st.button("🔄 Merge Records Now"):
    raw_df = load_data_from_sheet(sheet)
    merged_df = merge_start_stop(raw_df)
    if not merged_df.empty:
        save_merged_data_to_sheet(merged_df, spreadsheet, sheet_name=MERGED_SHEET)
        st.success("✅ Merged records saved.")
    else:
        st.warning("⚠ No records matched to merge.")

# === Edit/Delete Merged Records ===
st.markdown("## ✏️ Edit or 🗑️ Delete a Merged Record")

merged_data = load_data_from_sheet(sheet_name=MERGED_SHEET)

if merged_data.empty:
    st.info("No merged records available.")
else:
    merged_data["Row Number"] = merged_data.index + 2
    merged_data["Record ID"] = merged_data.apply(
        lambda x: f"{x['ID']} | {x['Site']} | {x['Start Date']} {x['Start Time']} - {x['Stop Date']} {x['Stop Time']}",
        axis=1
    )

    selected = st.selectbox("Select a merged record to edit or delete:", [""] + merged_data["Record ID"].tolist())

    if selected:
        idx = merged_data[merged_data["Record ID"] == selected].index[0]
        row = merged_data.loc[idx]
        row_num = row["Row Number"]

        with st.form("edit_merged_form"):
            new_pm25 = st.number_input("PM₂.₅ (µg/m³)", value=float(row.get("PM2.5 (µg/m³)", 0)), step=0.1)
            new_notes = st.text_area("Notes", value=row.get("Notes", ""))
            submitted = st.form_submit_button("✅ Update Record")

            if submitted:
                ws = spreadsheet.worksheet(MERGED_SHEET)
                ws.update_cell(row_num, merged_data.columns.get_loc("PM2.5 (µg/m³)") + 1, new_pm25)
                ws.update_cell(row_num, merged_data.columns.get_loc("Notes") + 1, new_notes)
                st.success("✅ Merged record updated.")
                st.experimental_rerun()

        st.markdown("### Danger Zone 🚨")
        if st.checkbox("Confirm deletion of this record"):
            if st.button("🗑️ Delete Merged Record"):
                ws = spreadsheet.worksheet(MERGED_SHEET)
                ws.delete_rows(row_num)
                st.success("✅ Merged record deleted.")
                st.experimental_rerun()

# --- Footer ---
st.markdown("""
    <hr style="margin-top: 40px; margin-bottom:10px">
    <div style='text-align: center; color: grey; font-size: 0.9em;'>
        © 2025 EPA Ghana · Developed by Clement Mensah Ackaah · Built with ❤️ using Streamlit
    </div>
""", unsafe_allow_html=True)
