# data entry.pyimport streamlit as st
import pandas as pd
import streamlit as st
from datetime import datetime
from utils import load_data_from_sheet, add_data, merge_start_stop,save_merged_data_to_sheet,sheet,spreadsheet,filter_dataframe,display_and_merge_data,delete_row,delete_merged_record_by_index
from constants import MERGED_SHEET, MAIN_SHEET, SPREADSHEET_ID



ids = ["",'1', '2', '3','4','5','6','7','8','9','10']
sites = ["",'Kaneshie First Light', 'Tetteh Quarshie', 'Achimota', 'La','Mallam Market','Graphic Road','Weija','Tantra Hill', 'Amasaman']
officers = ['Obed', 'Clement', 'Peter','Ben','Mawuli']

# Entry Type Selection
entry_type = st.selectbox("Select Entry Type", ["", "START", "STOP"])

if entry_type:
    id_selected = st.selectbox("Select Site ID", ids)
    site_selected = st.selectbox("Select Site", sites)
    officer_selected = st.multiselect("Monitoring Officer(s)", officers)
    driver_name = st.text_input("Driver's Name")

# === Start Day Observation ===
if entry_type == "START":
    with st.expander("Start Day Monitoring", expanded=True):
        start_date = st.date_input("Start Date", value=datetime.today())
        start_obs = st.text_area("First Day Observation")

        st.markdown("#### Initial Atmospheric Conditions")
        start_temp = st.number_input("Temperature (°C)", step=0.1)
        start_rh = st.number_input("Relative Humidity (%)", step=0.1)
        start_pressure = st.number_input("Pressure (mbar)", step=0.1)
        start_weather = st.text_input("Weather")
        start_wind = st.text_input("Wind Speed and Direction")

        st.markdown("#### Initial Sampler Information")
        start_elapsed = st.number_input("Initial Elapsed Time (min)", step=1)
        start_flow = st.number_input("Initial Flow Rate (L/min)", step=0.1)
        start_time = st.time_input("Start Time", value=datetime.now().time())

        if st.button("Submit Start Day Data"):
            if all([id_selected, site_selected, officer_selected, driver_name]):
                start_row = [
                    "START", id_selected, site_selected, ", ".join(officer_selected), driver_name,
                    start_date.strftime("%Y-%m-%d"), start_time.strftime("%H:%M:%S"),
                    start_temp, start_rh, start_pressure, start_weather, start_wind,
                    start_elapsed, start_flow, start_obs
                ]
                add_data(start_row)
                st.success("Start day data submitted successfully!")
            else:
                st.error("Please complete all required fields.")

# === Stop Day Observation ===
elif entry_type == "STOP":
    with st.expander("Stop Day Monitoring", expanded=True):
        stop_date = st.date_input("Stop Date", value=datetime.today())
        stop_obs = st.text_area("Final Day Observation")

        st.markdown("#### Final Atmospheric Conditions")
        stop_temp = st.number_input("Final Temperature (°C)", step=0.1)
        stop_rh = st.number_input("Final Relative Humidity (%)", step=0.1)
        stop_pressure = st.number_input("Final Pressure (mbar)", step=0.1)
        stop_weather = st.text_input("Final Weather")
        stop_wind = st.text_input("Final Wind Speed and Direction")

        st.markdown("#### Final Sampler Information")
        stop_elapsed = st.number_input("Final Elapsed Time (min)", step=1)
        stop_flow = st.number_input("Final Flow Rate (L/min)", step=0.1)
        stop_time = st.time_input("Stop Time", value=datetime.now().time())

        if st.button("Submit Stop Day Data"):
            if all([id_selected, site_selected, officer_selected, driver_name]):
                stop_row = [
                    "STOP", id_selected, site_selected, ", ".join(officer_selected), driver_name,
                    stop_date.strftime("%Y-%m-%d"), stop_time.strftime("%H:%M:%S"),
                    stop_temp, stop_rh, stop_pressure, stop_weather, stop_wind,
                    stop_elapsed, stop_flow, stop_obs
                ]
                add_data(stop_row)
                st.success("Stop day data submitted successfully!")
            else:
                st.error("Please complete all required fields.")

# === Display & Merge Records ===
st.header("Submitted Monitoring Records")
df = load_data_from_sheet(sheet)
display_and_merge_data(df, spreadsheet, MERGED_SHEET)

# === Delete Submitted Records ===
st.subheader("🗑️ Delete Submitted Record")
if not df.empty:
    df["Submitted At"] = pd.to_datetime(df["Submitted At"], errors="coerce")
    df["Record Label"] = df.apply(
        lambda x: f"{x['Entry Type']} | {x['ID']} | {x['Site']} | {x['Submitted At'].strftime('%Y-%m-%d %H:%M')}",
        axis=1
    )
    selected_to_delete = st.selectbox("Select a submitted record to delete", [""] + df["Record Label"].tolist())

    if selected_to_delete:
        with st.form("delete_submitted_form"):
            st.warning("Are you sure you want to delete this submitted record?")
            confirm = st.form_submit_button("🗑️ Delete Submitted Record")
            if confirm:
                idx = df[df["Record Label"] == selected_to_delete].index[0]
                row_number = idx + 2  # Adjust for header
                delete_row(sheet, row_number)
                st.success("Submitted record deleted.")

# === Delete Merged Records ===
st.subheader("🗑️ Delete Merged Record")
merged_df = merge_start_stop(df)
if not merged_df.empty:
    merged_df["Record Label"] = merged_df.apply(
        lambda x: f"{x['ID']} | {x['Site']} | {x['Start Date']} - {x['Stop Date']}", axis=1
    )
    selected_merged_to_delete = st.selectbox("Select a merged record to delete", [""] + merged_df["Record Label"].tolist())

    if selected_merged_to_delete:
        with st.form("delete_merged_form"):
            st.warning("Are you sure you want to delete this merged record?")
            confirm_merged = st.form_submit_button("🗑️ Delete Merged Record")
            if confirm_merged:
                idx = merged_df[merged_df["Record Label"] == selected_merged_to_delete].index[0]
                delete_merged_record_by_index(spreadsheet, MERGED_SHEET, idx)
                st.success("Merged record deleted.")

st.markdown("""
    <hr style="margin-top: 40px; margin-bottom:10px">
    <div style='text-align: center; color: grey; font-size: 0.9em;'>
        © 2025 EPA Ghana· Developed by Clement Mensah Ackaah· Built with ❤️ using Streamlit
    </div>
""", unsafe_allow_html=True)
