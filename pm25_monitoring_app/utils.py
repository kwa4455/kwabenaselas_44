import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
from constants import SPREADSHEET_ID, MAIN_SHEET, MERGED_SHEET

# === Google Sheets Setup ===
def setup_google_sheets():
    """Authenticate and return the spreadsheet object."""
    creds_json = st.secrets["GOOGLE_CREDENTIALS"]
    creds_dict = json.loads(creds_json)

    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive.file",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    return client.open_by_key(SPREADSHEET_ID)

# Initialize spreadsheet and ensure MAIN_SHEET exists
spreadsheet = setup_google_sheets()

try:
    sheet = spreadsheet.worksheet(MAIN_SHEET)
except gspread.WorksheetNotFound:
    sheet = spreadsheet.add_worksheet(title=MAIN_SHEET, rows="100", cols="20")
    sheet.append_row([
        "Entry Type", "ID", "Site", "Monitoring Officer", "Driver",
        "Date", "Time", "Temperature (°C)", "RH (%)", "Pressure (mbar)",
        "Weather", "Wind", "Elapsed Time (min)", "Flow Rate (L/min)", "Observation",
        "Submitted At"
    ])

# === Utility Functions ===

def convert_timestamps_to_string(df):
    """Convert all datetime columns in a DataFrame to strings."""
    for column in df.select_dtypes(include=['datetime64[ns]']).columns:
        df[column] = df[column].dt.strftime('%Y-%m-%d %H:%M:%S')
    return df

def load_data_from_sheet(sheet):
    """Load all data from the given worksheet into a DataFrame."""
    data = sheet.get_all_records()
    df = pd.DataFrame(data)
    return convert_timestamps_to_string(df)

def add_data(row):
    """Append a row with timestamp to the main worksheet."""
    row.append(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    sheet.append_row(row)

def merge_start_stop(df):
    """Merge START and STOP records based on ID and Site."""
    start_df = df[df["Entry Type"] == "START"].copy()
    stop_df = df[df["Entry Type"] == "STOP"].copy()

    merge_keys = ["ID", "Site"]
    start_df = start_df.rename(columns=lambda x: f"{x}_Start" if x not in merge_keys else x)
    stop_df = stop_df.rename(columns=lambda x: f"{x}_Stop" if x not in merge_keys else x)

    merged_df = pd.merge(start_df, stop_df, on=merge_keys, how="inner")

    if "Elapsed Time (min)_Start" in merged_df.columns and "Elapsed Time (min)_Stop" in merged_df.columns:
        merged_df["Elapsed Time Diff (min)"] = (
            merged_df["Elapsed Time (min)_Stop"] - merged_df["Elapsed Time (min)_Start"]
        )

    return merged_df

def save_merged_data_to_sheet(df, spreadsheet, sheet_name):
    """Save merged data to a specified worksheet."""
    df = convert_timestamps_to_string(df)

    if sheet_name in [ws.title for ws in spreadsheet.worksheets()]:
        spreadsheet.del_worksheet(spreadsheet.worksheet(sheet_name))

    new_sheet = spreadsheet.add_worksheet(title=sheet_name, rows="1000", cols="50")
    new_sheet.update([df.columns.tolist()] + df.values.tolist())

def filter_dataframe(df, site_filter=None, date_range=None):
    """Filter the DataFrame by site and date range."""
    if df.empty:
        return df

    if "Submitted At" in df.columns:
        df["Submitted At"] = pd.to_datetime(df["Submitted At"], errors="coerce")

    if site_filter and site_filter != "All":
        df = df[df["Site"] == site_filter]

    if date_range and len(date_range) == 2:
        start, end = date_range
        df = df[(df["Submitted At"].dt.date >= start) & (df["Submitted At"].dt.date <= end)]

    return df



def delete_row(sheet, row_number):
    sheet.delete_rows(row_number)

# --- Inside your edit_submitted_record function or wherever applicable ---
# After the Update button in the form:
if st.form_submit_button("🗑️ Delete Record"):
    try:
        sheet.delete_rows(row_number)
        st.success("Record deleted successfully!")
        st.session_state.selected_record = None
        st.session_state.edit_expanded = False

        handle_merge_logic(
            sheet=sheet,
            spreadsheet=spreadsheet,
            merged_sheet_name=merged_sheet_name,
            load_data_from_sheet=load_data_from_sheet,
            merge_start_stop=merge_start_stop,
            save_merged_data_to_sheet=save_merged_data_to_sheet
        )

    except Exception as e:
        st.error(f"Failed to delete record: {e}")

# --- For deleting from Merged Sheet directly (if needed) ---
def delete_merged_record_by_index(merged_sheet, index):
    # Add +2 because Google Sheets is 1-indexed and row 1 is the header
    merged_sheet.delete_rows(index + 2)

# --- UI in data entry app to optionally delete from merged records ---
with st.expander("🗑️ Delete Merged Record"):
    merged_sheet = spreadsheet.worksheet(MERGED_SHEET)
    merged_df = pd.DataFrame(merged_sheet.get_all_records())
    if not merged_df.empty:
        merged_df["Row Number"] = merged_df.index + 2
        merged_df["Merged Record"] = merged_df.apply(lambda x: f"{x['ID']} | {x['Site']} | {x['Date_Start']} -> {x['Date_Stop']}", axis=1)

        to_delete = st.selectbox("Select merged record to delete", [""] + merged_df["Merged Record"].tolist())
        if to_delete:
            row_index = merged_df[merged_df["Merged Record"] == to_delete].index[0]
            if st.button("Delete Selected Merged Record"):
                delete_merged_record_by_index(merged_sheet, row_index)
                st.success("Merged record deleted.")
    else:
        st.info("No merged records found.")



def display_and_merge_data(df, spreadsheet, merged_sheet_name):
    """Display data in Streamlit, filter it, and merge start/stop records."""
    if df.empty:
        st.info("No data submitted yet.")
        return

    with st.expander("🔍 Filter Records"):
        site_filter = st.selectbox("Filter by Site", ["All"] + sorted(df["Site"].dropna().unique()))
        date_range = st.date_input("Filter by Date Range", [])

    filtered_df = filter_dataframe(df, site_filter, date_range)
    st.dataframe(filtered_df, use_container_width=True)

    merged_df = merge_start_stop(filtered_df)
    if not merged_df.empty:
        save_merged_data_to_sheet(merged_df, spreadsheet, merged_sheet_name)
        st.success("Merged records saved to Google Sheets.")
        st.dataframe(merged_df, use_container_width=True)
    else:
        st.warning("No matching START and STOP records found to merge.")
