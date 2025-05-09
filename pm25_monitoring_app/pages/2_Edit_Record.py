import pandas as pd
import streamlit as st
from datetime import datetime
from utils import load_data_from_sheet, add_data, merge_start_stop,save_merged_data_to_sheet,sheet,spreadsheet,filter_dataframe,display_and_merge_data,display_and_merge_data,save_merged_data_to_sheet,convert_timestamps_to_string
from constants import MERGED_SHEET, MAIN_SHEET, SPREADSHEET_ID

df = load_data_from_sheet(sheet)

# Convert to datetime if not already
df["Submitted At"] = pd.to_datetime(df["Submitted At"], errors='coerce')

# Initialize session state
if 'selected_record' not in st.session_state:
    st.session_state.selected_record = None
if 'edit_expanded' not in st.session_state:
    st.session_state.edit_expanded = False

if df.empty:
    st.warning("No records available to edit.")
else:
    df["Row Number"] = df.index + 2
    df["Record ID"] = df.apply(
        lambda x: f"{x['Entry Type']} | {x['ID']} | {x['Site']} | {x['Submitted At'].strftime('%Y-%m-%d %H:%M')}",
        axis=1
    )

    record_options = [""] + df["Record ID"].tolist()
    selected = st.selectbox("Select a record to edit:", record_options, index=record_options.index(st.session_state.selected_record) if st.session_state.selected_record in record_options else 0)

    if selected and selected != st.session_state.selected_record:
        st.session_state.selected_record = selected
        st.session_state.edit_expanded = True

    with st.expander("✏️ Edit Submitted Record", expanded=st.session_state.edit_expanded):
        if not st.session_state.selected_record:
            st.info("Please select a record.")
        else:
            try:
                selected_index = df[df["Record ID"] == st.session_state.selected_record].index[0]
                record_data = df.loc[selected_index]
                row_number = record_data["Row Number"]

                with st.form("edit_form"):
                    entry_type = st.selectbox("Entry Type", ["START", "STOP"], index=["START", "STOP"].index(record_data["Entry Type"]))
                    site_id = st.text_input("ID", value=record_data["ID"])
                    site = st.text_input("Site", value=record_data["Site"])
                    monitoring_officer = st.text_input("Monitoring Officer", value=record_data["Monitoring Officer"])
                    driver = st.text_input("Driver", value=record_data["Driver"])
                    date = st.date_input("Date", value=pd.to_datetime(record_data["Date"]))
                    time = st.time_input("Time", value=pd.to_datetime(record_data["Time"]).time())
                    temperature = st.number_input("Temperature (°C)", value=float(record_data["Temperature (°C)"]), step=0.1)
                    rh = st.number_input("Relative Humidity (%)", value=float(record_data["RH (%)"]), step=0.1)
                    pressure = st.number_input("Pressure (mbar)", value=float(record_data["Pressure (mbar)"]), step=0.1)
                    weather = st.text_input("Weather", value=record_data["Weather"])
                    wind = st.text_input("Wind", value=record_data["Wind"])
                    elapsed_time = st.number_input("Elapsed Time (min)", value=float(record_data["Elapsed Time (min)"]), step=1.0)
                    flow_rate = st.number_input("Flow Rate (L/min)", value=float(record_data["Flow Rate (L/min)"]), step=0.1)
                    observation = st.text_area("Observation", value=record_data.get("Observation", ""))

                    submitted = st.form_submit_button("Update Record")

                    if submitted:
                        updated_data = [
                            entry_type, site_id, site, monitoring_officer, driver,
                            date.strftime("%Y-%m-%d"), time.strftime("%H:%M:%S"),
                            temperature, rh, pressure, weather, wind,
                            elapsed_time, flow_rate, observation
                        ]

                        for col_index, value in enumerate(updated_data, start=1):
                            sheet.update_cell(row_number, col_index, value)

                        st.success("Record updated successfully!")

                        # Reset state to collapse
                        st.session_state.selected_record = None
                        st.session_state.edit_expanded = False

                        # Reload and merge
                        df = load_data_from_sheet(sheet)
                        merged_df = merge_start_stop(df)
                        if not merged_df.empty:
                            save_merged_data_to_sheet(merged_df, spreadsheet, sheet_name=merged_sheet_name)
                            st.success("Merged records updated.")
                            st.dataframe(merged_df, use_container_width=True)
                        else:
                            st.warning("No matching records to merge.")

            except Exception as e:
                st.error(f"Error: {e}")
edit_submitted_record(
    df=df,
    sheet=sheet,
    spreadsheet=spreadsheet,
    merged_sheet_name=MERGED_SHEET,
    load_data_from_sheet=load_data_from_sheet,
    merge_start_stop=merge_start_stop,
    save_merged_data_to_sheet=save_merged_data_to_sheet
)


st.markdown("""
    <hr style="margin-top: 40px; margin-bottom:10px">
    <div style='text-align: center; color: grey; font-size: 0.9em;'>
        © 2025 EPA Ghana· Developed by Clement Mensah Ackaah· Built with ❤️ using Streamlit
    </div>
""", unsafe_allow_html=True)
