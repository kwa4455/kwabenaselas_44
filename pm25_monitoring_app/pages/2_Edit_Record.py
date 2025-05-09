import pandas as pd
import streamlit as st
from datetime import datetime

def generate_record_id(row):
    """Generate a unique record ID."""
    try:
        timestamp = row['Submitted At']
        # Handle invalid timestamp
        if pd.notnull(timestamp):
            timestamp_str = timestamp.strftime('%Y-%m-%d %H:%M')  # Format the timestamp
        else:
            timestamp_str = "Invalid Date"
        return f"{row['Entry Type']} | {row['ID']} | {row['Site']} | {timestamp_str}"
    except Exception as e:
        # Return a more informative error if it occurs
        return f"Invalid Record | Error: {e}"

def render_edit_form(record_data):
    """Render the form for editing a record."""
    with st.form("edit_form"):
        entry_type = st.selectbox("Entry Type", ["START", "STOP"], index=["START", "STOP"].index(record_data["Entry Type"]))
        site_id = st.text_input("ID", value=record_data["ID"])
        site = st.text_input("Site", value=record_data["Site"])
        monitoring_officer = st.text_input("Monitoring Officer", value=record_data["Monitoring Officer"])
        driver = st.text_input("Driver", value=record_data["Driver"])
        
        # Ensure date and time inputs are handled correctly
        date = st.date_input("Date", value=pd.to_datetime(record_data["Date"]) if pd.notnull(record_data["Date"]) else datetime.today())
        time = st.time_input("Time", value=pd.to_datetime(record_data["Time"]).time() if pd.notnull(record_data["Time"]) else datetime.now().time())
        
        temperature = st.number_input("Temperature (°C)", value=float(record_data["Temperature (°C)"]), step=0.1)
        rh = st.number_input("Relative Humidity (%)", value=float(record_data["RH (%)"]), step=0.1)
        pressure = st.number_input("Pressure (mbar)", value=float(record_data["Pressure (mbar)"]), step=0.1)
        weather = st.text_input("Weather", value=record_data["Weather"])
        wind = st.text_input("Wind", value=record_data["Wind"])
        elapsed_time = st.number_input("Elapsed Time (min)", value=float(record_data["Elapsed Time (min)"]), step=1.0)
        flow_rate = st.number_input("Flow Rate (L/min)", value=float(record_data["Flow Rate (L/min)"]), step=0.1)
        observation = st.text_area("Observation", value=record_data.get("Observation", ""))
        
        submitted = st.form_submit_button("Update Record")
        return submitted, {
            "entry_type": entry_type, "site_id": site_id, "site": site,
            "monitoring_officer": monitoring_officer, "driver": driver,
            "date": date, "time": time, "temperature": temperature,
            "rh": rh, "pressure": pressure, "weather": weather,
            "wind": wind, "elapsed_time": elapsed_time,
            "flow_rate": flow_rate, "observation": observation
        }

def edit_submitted_record(df, sheet, spreadsheet, merged_sheet_name, load_data_from_sheet, merge_start_stop, save_merged_data_to_sheet):
    """Function to edit submitted records."""
    if "selected_record" not in st.session_state:
        st.session_state.selected_record = None
    if "edit_expanded" not in st.session_state:
        st.session_state.edit_expanded = False

    if df.empty:
        st.warning("No records available to edit.")
        return

    # Ensure proper data types
    df["Entry Type"] = df["Entry Type"].astype(str)
    df["ID"] = df["ID"].astype(str)
    df["Site"] = df["Site"].astype(str)
    
    # Handle invalid or missing dates in the "Submitted At" column
    df["Submitted At"] = pd.to_datetime(df["Submitted At"], errors="coerce")
    
    # Assign row numbers
    df["Row Number"] = df.index + 2

    # Generate unique Record ID
    df["Record ID"] = df.apply(generate_record_id, axis=1)
    record_options = [""] + df["Record ID"].tolist()

    selected = st.selectbox("Select a record to edit:", record_options, index=record_options.index(st.session_state.selected_record) if st.session_state.selected_record in record_options else 0)

    if selected and selected != st.session_state.selected_record:
        st.session_state.selected_record = selected
        st.session_state.edit_expanded = True

    with st.expander("✏️ Edit Submitted Records", expanded=st.session_state.edit_expanded):
        if not st.session_state.selected_record:
            st.info("Please select a record to edit.")
            return

        try:
            selected_index = df[df["Record ID"] == st.session_state.selected_record].index[0]
            record_data = df.loc[selected_index]
            row_number = record_data["Row Number"]

            submitted, updates = render_edit_form(record_data)

            if submitted:
                updated_data = [
                    updates["entry_type"], updates["site_id"], updates["site"],
                    updates["monitoring_officer"], updates["driver"],
                    updates["date"].strftime("%Y-%m-%d"),
                    updates["time"].strftime("%H:%M:%S"),
                    updates["temperature"], updates["rh"], updates["pressure"],
                    updates["weather"], updates["wind"],
                    updates["elapsed_time"], updates["flow_rate"],
                    updates["observation"]
                ]

                for col_index, value in enumerate(updated_data, start=1):
                    sheet.update_cell(row_number, col_index, value)

                st.success("Record updated successfully!")
                st.session_state.selected_record = None
                st.session_state.edit_expanded = False

                # Reload data and reapply necessary transformations
                df = load_data_from_sheet(sheet)
                df["Submitted At"] = pd.to_datetime(df["Submitted At"], errors="coerce")
                df["Row Number"] = df.index + 2
                df["Record ID"] = df.apply(generate_record_id, axis=1)

                # Merge start/stop records if applicable
                merged_df = merge_start_stop(df)
                if not merged_df.empty:
                    save_merged_data_to_sheet(merged_df, spreadsheet, sheet_name=merged_sheet_name)
                    st.success("Merged records saved to Google Sheets.")
                    st.dataframe(merged_df, use_container_width=True)
                else:
                    st.warning("No matching START and STOP records found to merge.")
        except Exception as e:
            st.error(f"An error occurred while editing: {e}")
