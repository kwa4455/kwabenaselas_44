import pandas as pd
import streamlit as st
from st_aggrid import AgGrid, GridUpdateMode
from st_aggrid.grid_options_builder import GridOptionsBuilder
from utils import (
    load_data_from_sheet,
    add_data,
    merge_start_stop,
    save_merged_data_to_sheet,
    delete_row,
    delete_merged_record_by_index,
    filter_by_site_and_date,
    backup_deleted_row,
    restore_specific_deleted_record,
    sheet,
    spreadsheet,
    display_and_merge_data,
    require_roles
)
from constants import MERGED_SHEET

st.set_page_config(page_title="Editor Tools", page_icon="✏️")
# Inject Google Fonts and custom CSS for glassmorphism and font clarity
st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap" rel="stylesheet">

    <style>
    /* === Global Font and Text Effects === */
    html, body, [class*="css"]  {
        font-family: 'Poppins', sans-serif;
        text-shadow: 0 1px 2px rgba(0,0,0,0.08);
        color: #1f1f1f;
        background-color: #f4f7fa;
    }

    /* === App Title Styling === */
    .main > div:first-child h1 {
        color: #0a3d62;
        font-size: 2.8rem;
        text-shadow: 0 2px 4px rgba(0,0,0,0.15);
        margin-bottom: 0.5rem;
    }

    /* === Sidebar Glass Effect === */
    section[data-testid="stSidebar"] {
        background: rgba(255, 255, 255, 0.12);
        backdrop-filter: blur(14px) saturate(160%);
        -webkit-backdrop-filter: blur(14px) saturate(160%);
        border: 1px solid rgba(255, 255, 255, 0.25);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.25);
    }

    /* === Sidebar Navigation Styling === */
    section[data-testid="stSidebar"] .st-radio > div {
        background: rgba(255, 255, 255, 0.85);
        color: #000;
        border-radius: 12px;
        padding: 0.4rem 0.6rem;
        margin-bottom: 0.5rem;
        transition: all 0.2s ease;
    }
    section[data-testid="stSidebar"] .st-radio > div:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
    }

    /* === Info box styling === */
    .stAlert {
        background-color: rgba(232, 244, 253, 0.9);
        border-left: 6px solid #1f77b4;
        border-radius: 8px;
        padding: 1rem;
    }

    /* === Success message styling === */
    .stSuccess {
        background-color: rgba(230, 255, 230, 0.9);
        border-left: 6px solid #33cc33;
        border-radius: 8px;
        padding: 1rem;
    }
    </style>
""", unsafe_allow_html=True)


st.markdown(
    """
    <div style='text-align: center;'>
        <h2>✏️ Editor Tools</h2>
        <p style='color: grey;'>This page allows authorized users to update or delete submitted records.</p>
    </div>
    <hr>
    """,
    unsafe_allow_html=True
)




require_roles("admin", "editor","collector")




def safe_float(val, default=0.0):
    try:
        return float(val)
    except (ValueError, TypeError):
        return default

def apply_filters(df, site_key="Site", date_key="Submitted At", label_prefix=""):
    with st.expander(f"🔍 Filter Records ({label_prefix})", expanded=True):
        site_filter = st.text_input(f"Filter by Site ({label_prefix})", "")
        date_filter = st.date_input(f"Filter by Date ({label_prefix})", None)

        if site_filter:
            df = df[df[site_key].str.contains(site_filter, case=False, na=False)]
        if date_filter:
            df[date_key] = pd.to_datetime(df[date_key], errors='coerce')
            df = df[df[date_key].dt.date == date_filter]

    return df


def render_record_edit_form(record_data):
    weather_options = ["Clear", "Cloudy", "Rainy", "Foggy", "Windy", "Hazy", "Dusty", "Other"]
    wind_dir_options = ["N", "NE", "E", "SE", "S", "SW", "W", "NW", "Variable", "Calm"]

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

    entry_type = st.selectbox("Entry Type", ["START", "STOP"], index=["START", "STOP"].index(get_str("Entry Type", "START")))
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
    weather = st.selectbox("Weather", weather_options, index=weather_options.index(weather_value) if weather_value in weather_options else len(weather_options) - 1)

    wind_speed = st.number_input("Wind Speed (m/s)", value=get_float("Wind Speed (m/s)"), step=0.1)
    wind_dir_value = get_str("Wind Direction", "Variable")
    wind_direction = st.selectbox("Wind Direction", wind_dir_options, index=wind_dir_options.index(wind_dir_value) if wind_dir_value in wind_dir_options else wind_dir_options.index("Variable"))

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


# --- Edit Submitted Record ---
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

    filtered_df = filter_by_site_and_date(df, context_label="(Edit)")

    if 'selected_record' not in st.session_state:
        st.session_state.selected_record = None
    if 'edit_expanded' not in st.session_state:
        st.session_state.edit_expanded = False

    record_options = [""] + filtered_df["Record ID"].tolist()
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
                selected_index = filtered_df[filtered_df["Record ID"] == st.session_state.selected_record].index[0]
                record_data = filtered_df.loc[selected_index]
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


# --- Delete Submitted Record ---
st.subheader("🗑️ Delete from Submitted Records")
df_submitted = load_data_from_sheet(sheet)

if df_submitted.empty:
    st.info("No submitted records available.")
else:
    df_submitted["Row Number"] = df_submitted.index + 2
    df_submitted["Submitted At"] = pd.to_datetime(df_submitted["Submitted At"], errors='coerce')
    df_submitted["Record ID"] = df_submitted.apply(
        lambda x: f"{x['Entry Type']} | {x['ID']} | {x['Site']} | {x['Submitted At']}", axis=1
    )

    filtered_df = filter_by_site_and_date(df_submitted, context_label="(Delete)")
    selected_record = st.selectbox("Select submitted record to delete:", [""] + filtered_df["Record ID"].tolist())

    if selected_record:
        row_to_delete = int(filtered_df[filtered_df["Record ID"] == selected_record]["Row Number"].values[0])

        if st.checkbox("✅ Confirm deletion of submitted record"):
            if st.button("🗑️ Delete Submitted Record"):
                deleted_by = st.session_state.username
                delete_row(sheet, row_to_delete, deleted_by)
                st.success(f"✅ Submitted record deleted by {deleted_by} and backed up successfully.")
                st.rerun()

st.markdown("---")
st.header("🗃️ Restore Deleted Record")

try:
    backup_sheet = spreadsheet.worksheet("Deleted Records")
    deleted_rows = backup_sheet.get_all_values()

    if len(deleted_rows) <= 1:
        st.info("No deleted records available.")
    else:
        headers = deleted_rows[0]
        records = deleted_rows[1:]

        df_deleted = pd.DataFrame(records, columns=headers)
        df_deleted["Submitted At"] = pd.to_datetime(df_deleted["Submitted At"], errors="coerce")

        filtered_deleted = filter_by_site_and_date(df_deleted, context_label="(Restore)")

        options = [
            f"{i + 1}. " + " | ".join(row[:-2]) + f" (Deleted by: {row[-1]})"
            for i, row in filtered_deleted.iterrows()
        ]
        selection_list = [""] + options

        selected = st.selectbox("Select a deleted record to restore:", selection_list)

        if st.button("↩️ Restore Selected Record", disabled=(selected == "")):
            selected_index = filtered_deleted.index[options.index(selected) - 1]
            result = restore_specific_deleted_record(selected_index)
            if "✅" in result:
                st.success(result)
                st.rerun()
            else:
                st.error(result)

except Exception as e:
    st.error(f"Failed to load deleted records: {e}")



# --- Footer ---
st.markdown("""
    <hr style="margin-top: 40px; margin-bottom:10px">
    <div style='text-align: center; color: grey; font-size: 0.9em;'>
        © 2025 EPA Ghana · Developed by Clement Mensah Ackaah · Built with ❤️ using Streamlit
    </div>
""", unsafe_allow_html=True)
