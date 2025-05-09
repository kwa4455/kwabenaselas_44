import pandas as pd
import streamlit as st
from constants import MERGED_SHEET, MAIN_SHEET, SPREADSHEET_ID
from utils import load_data_from_sheet, add_data, merge_start_stop,save_merged_data_to_sheet,sheet,spreadsheet

# Function to Edit Submitted Records
def edit_submitted_record(df, sheet, spreadsheet, merged_sheet_name, load_data_from_sheet, merge_start_stop, save_merged_data_to_sheet):
    # Initialize session state to track record selection and expander state
    if "selected_record" not in st.session_state:
        st.session_state.selected_record = None
    if "edit_expanded" not in st.session_state:
        st.session_state.edit_expanded = False

    if df.empty:
        st.warning("No records available to edit.")
        return

    # Add metadata to DataFrame for easy record identification
    df["Entry Type"] = df["Entry Type"].astype(str)
    df["ID"] = df["ID"].astype(str)
    df["Site"] = df["Site"].astype(str)
    df["Record ID"] = df.apply(
        lambda x: f"{x['Entry Type']} | {x['ID']} | {x['Site']} | {x['Submitted At'].strftime('%Y-%m-%d %H:%M')}",
        axis=1
    )

    # Select a record to edit
    record_options = [""] + df["Record ID"].tolist()
    selected = st.selectbox("Select a record to edit:", record_options, index=record_options.index(st.session_state.selected_record))

    # Update selected record and expander state
    if selected and selected != st.session_state.selected_record:
        st.session_state.selected_record = selected
        st.session_state.edit_expanded = True  # Expand the section when a record is selected

    # Edit section (Expander) that toggles based on state
    with st.expander("✏️ Edit Submitted Records", expanded=st.session_state.edit_expanded):
        if not st.session_state.selected_record:
            st.info("Please select a record to edit.")
            return

        try:
            # Find the selected record
            selected_index = df[df["Record ID"] == st.session_state.selected_record].index[0]
            record_data = df.loc[selected_index]
            row_number = record_data["Row Number"]

            # Create a form to edit the selected record
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

                # When user submits the form
                if submitted:
                    updated_data = [
                        entry_type, site_id, site, monitoring_officer, driver,
                        date.strftime("%Y-%m-%d"), time.strftime("%H:%M:%S"),
                        temperature, rh, pressure, weather, wind,
                        elapsed_time, flow_rate, observation
                    ]

                    # Update the record in the Google Sheets
                    for col_index, value in enumerate(updated_data, start=1):
                        sheet.update_cell(row_number, col_index, value)

                    st.success("Record updated successfully!")

                    # Reset session state (collapse the expander and reset selection)
                    st.session_state.selected_record = None
                    st.session_state.edit_expanded = False

                    # Reload the data and merge START/STOP records
                    df = load_data_from_sheet(sheet)
                    df["Row Number"] = df.index + 2
                    df["Record ID"] = df.apply(
                        lambda x: f"{x['Entry Type']} | {x['ID']} | {x['Site']} | {x['Submitted At'].strftime('%Y-%m-%d %H:%M')}",
                        axis=1
                    )

                    # Merge the data if applicable
                    merged_df = merge_start_stop(df)
                    if not merged_df.empty:
                        save_merged_data_to_sheet(merged_df, spreadsheet, sheet_name=merged_sheet_name)
                        st.success("Merged records saved to Google Sheets.")
                        st.dataframe(merged_df, use_container_width=True)
                    else:
                        st.warning("No matching START and STOP records found to merge.")
        except Exception as e:
            st.error(f"An error occurred while editing: {e}")


df = load_data_from_sheet(sheet)
edit_submitted_record(
    df=df,
    sheet=sheet,
    spreadsheet=spreadsheet,
    merged_sheet_name=MERGED_SHEET,
    load_data_from_sheet=load_data_from_sheet,
    merge_start_stop=merge_start_stop,
    save_merged_data_to_sheet=save_merged_data_to_sheet
)
