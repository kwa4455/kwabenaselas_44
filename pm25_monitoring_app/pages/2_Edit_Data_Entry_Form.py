import pandas as pd
import streamlit as st
from utils import (
    load_data_from_sheet,
    add_data,
    merge_start_stop,
    save_merged_data_to_sheet,
    delete_row,
    delete_merged_record_by_index,
    backup_deleted_row,
    sheet,
    spreadsheet,
    display_and_merge_data,
    require_roles
)
from constants import MERGED_SHEET

# --- Page Title ---
st.title("✏️ Editor Tools")
st.write("This page will display records and allow authorized users to delete or update them.")



require_roles("admin", "editor","collector")



# --- Utility Functions ---
def safe_float(val, default=0.0):
    try:
        return float(val)
    except (ValueError, TypeError):
        return default

def render_record_edit_form(record_data):
    weather_options = ["Clear", "Cloudy", "Rainy", "Foggy", "Windy", "Hazy", "Dusty", "Other"]
    wind_dir_options = ["N", "NE", "E", "SE", "S", "SW", "W", "NW", "Variable", "Calm"]

    # Safe defaults
    def get_str(key, default=""):
        return str(record_data.get(key, default))

    def get_float(key, default=0.0):
        try:
            return float(record_data.get(key, default))
        except (ValueError, TypeError):
            return default

    def get_date(key):
        try:
            return pd.to_datetime(record_data.get(key)).date()
        except Exception:
            return pd.Timestamp.now().date()

    def get_time(key):
        try:
            return pd.to_datetime(record_data.get(key)).time()
        except Exception:
            return pd.Timestamp.now().time()

    entry_type = st.selectbox(
        "Entry Type",
        ["START", "STOP"],
        index=["START", "STOP"].index(get_str("Entry Type", "START"))
    )

    site_id = st.text_input("ID", value=get_str("ID"))
    site = st.text_input("Site", value=get_str("Site"))
    monitoring_officer = st.text_input("Monitoring Officer", value=get_str("Monitoring Officer"))
    driver = st.text_input("Driver", value=get_str("Driver"))
    date = st.date_input("Date", value=get_date("Date"))
    time = st.time_input("Time", value=get_time("Time"))
    temperature = st.number_input("Temperature (°C)", value=get_float("Temperature (°C)"), step=0.1)
    rh = st.number_input("Relative Humidity (%)", value=get_float("RH (%)"), step=0.1)
    pressure = st.number_input("Pressure (mbar)", value=get_float("Pressure (mbar)"), step=0.1)

    weather_value = get_str("Weather", "Other")
    weather = st.selectbox(
        "Weather", 
        weather_options,
        index=weather_options.index(weather_value) if weather_value in weather_options else len(weather_options) - 1
    )

    wind_speed = st.number_input("Wind Speed (m/s)", value=get_float("Wind Speed (m/s)"), step=0.1)

    wind_dir_value = get_str("Wind Direction", "Variable")
    wind_direction = st.selectbox(
        "Wind Direction",
        wind_dir_options,
        index=wind_dir_options.index(wind_dir_value) if wind_dir_value in wind_dir_options else wind_dir_options.index("Variable")
    )

    elapsed_time = st.number_input("Elapsed Time (min)", value=get_float("Elapsed Time (min)"), step=1.0)
    flow_rate = st.number_input("Flow Rate (L/min)", value=get_float("Flow Rate (L/min)"), step=0.1)
    observation = st.text_area("Observation", value=get_str("Observation"))

    return [
        entry_type, site_id, site, monitoring_officer, driver,
        date.strftime("%Y-%m-%d"), time.strftime("%H:%M:%S"),
        temperature, rh, pressure, weather,
        wind_speed, wind_direction,
        elapsed_time, flow_rate, observation
    ]

def make_unique_headers(headers):
    """
    Ensure headers are unique by appending '.1', '.2', etc. to duplicates.
    """
    seen = {}
    unique_headers = []
    for h in headers:
        if h == '':
            h = 'Unnamed'
        if h in seen:
            seen[h] += 1
            unique_headers.append(f"{h}.{seen[h]}")
        else:
            seen[h] = 0
            unique_headers.append(h)
    return unique_headers


def handle_merge_logic():
    df = load_data_from_sheet(sheet)
    merged_df = merge_start_stop(df)

    if not merged_df.empty:
        save_merged_data_to_sheet(merged_df, spreadsheet, sheet_name=MERGED_SHEET)
        st.success("✅ Merged records updated.")
        st.dataframe(merged_df, use_container_width=True)
    else:
        st.warning("⚠ No matching records to merge.")

def edit_submitted_record():
    df = load_data_from_sheet(sheet)

    if df.empty:
        st.warning("⚠ No records available to edit.")
        return

    df["Submitted At"] = pd.to_datetime(df["Submitted At"], errors='coerce')
    df["Row Number"] = df.index + 2
    df["Record ID"] = df.apply(
        lambda x: f"{x['Entry Type']} | {x['ID']} | {x['Site']} | {x['Submitted At'].strftime('%Y-%m-%d %H:%M')}",
        axis=1
    )

    if 'selected_record' not in st.session_state:
        st.session_state.selected_record = None
    if 'edit_expanded' not in st.session_state:
        st.session_state.edit_expanded = False

    record_options = [""] + df["Record ID"].tolist()
    selected = st.selectbox(
        "Select a record to edit:",
        record_options,
        index=record_options.index(st.session_state.selected_record) if st.session_state.selected_record in record_options else 0
    )

    if selected and selected != st.session_state.selected_record:
        st.session_state.selected_record = selected
        st.session_state.edit_expanded = True

    with st.expander("✏️ Edit Submitted Record", expanded=st.session_state.edit_expanded):
        if not st.session_state.selected_record:
            st.info("ℹ️ Please select a record from the dropdown above.")
        else:
            try:
                selected_index = df[df["Record ID"] == st.session_state.selected_record].index[0]
                record_data = df.loc[selected_index]
                row_number = record_data["Row Number"]

                with st.form("edit_form"):
                    updated_data = render_record_edit_form(record_data)
                    submitted = st.form_submit_button("Update Record")

                    if submitted:
                        for col_index, value in enumerate(updated_data, start=1):
                            sheet.update_cell(row_number, col_index, value)

                        st.success("✅ Record updated successfully!")
                        st.session_state.selected_record = None
                        st.session_state.edit_expanded = False

                        handle_merge_logic()
            except Exception as e:
                st.error(f"❌ Error: {e}")

# --- Run Editor Logic ---
edit_submitted_record()
# --- Delete from Submitted Records ---
st.subheader("🗑️ Delete from Submitted Records")
df_submitted = load_data_from_sheet(sheet)

if df_submitted.empty:
    st.info("No submitted records available.")
else:
    df_submitted["Row Number"] = df_submitted.index + 2  # Google Sheets is 1-indexed + header
    df_submitted["Record ID"] = df_submitted.apply(
        lambda x: f"{x['Entry Type']} | {x['ID']} | {x['Site']} | {x['Submitted At']}", axis=1
    )

    selected_record = st.selectbox("Select submitted record to delete:", [""] + df_submitted["Record ID"].tolist())

    if selected_record:
        row_to_delete = int(df_submitted[df_submitted["Record ID"] == selected_record]["Row Number"].values[0])
        
        if st.checkbox("✅ Confirm deletion of submitted record"):
            if st.button("🗑️ Delete Submitted Record"):
                delete_row(sheet, row_to_delete)
                st.success("✅ Submitted record deleted and backed up successfully.")
                st.rerun()



# --- Footer ---
st.markdown("""
    <hr style="margin-top: 40px; margin-bottom:10px">
    <div style='text-align: center; color: grey; font-size: 0.9em;'>
        © 2025 EPA Ghana · Developed by Clement Mensah Ackaah · Built with ❤️ using Streamlit
    </div>
""", unsafe_allow_html=True)
