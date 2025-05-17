import streamlit as st
import pandas as pd
import gspread
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials
import json
import time
from constants import SPREADSHEET_ID, MAIN_SHEET, MERGED_SHEET, CALC_SHEET

# === Google Sheets Setup ===
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

spreadsheet = client.open_by_key(SPREADSHEET_ID)


# === Ensure Observations worksheet exists and is initialized ===
def ensure_main_sheet_initialized(spreadsheet, sheet_name):
    try:
        sheet = spreadsheet.worksheet(sheet_name)
    except gspread.WorksheetNotFound:
        sheet = spreadsheet.add_worksheet(title=sheet_name, rows="100", cols="20")

    if not sheet.get_all_values():
        sheet.append_row([
            "Entry Type", "ID", "Site", "Monitoring Officer", "Driver",
            "Date", "Time", "Temperature (°C)", "RH (%)", "Pressure (mbar)",
            "Weather", "Wind Speed", "Wind Direction", "Elapsed Time (min)", "Flow Rate (L/min)", "Observation",
            "Submitted At"
        ])
    return sheet

sheet = ensure_main_sheet_initialized(spreadsheet, MAIN_SHEET)

# === User Management ===
USERS = {
    "clement": {"password": "admin123", "role": "admin", "email": "clement@epa.gov.gh"},
    "peter": {"password": "peter123", "role": "editor", "email": "peter@epa.gov.gh"},
    "ben": {"password": "ben123", "role": "editor", "email": "peter@epa.gov.gh"},
    "moses": {"password": "moses123", "role": "collector", "email": "peter@epa.gov.gh"},
    "john_G": {"password": "john123", "role": "collector", "email": "peter@epa.gov.gh"},
    "mawuli": {"password": "mawuli123", "role": "editor", "email": "mawuli@epa.gov.gh"},
    "obed": {"password": "viewer123", "role": "editor", "email": "obed@epa.gov.gh"},
    "maxwell": {"password": "maxwell123", "role": "viewer", "email": "obed@epa.gov.gh"},
    "selina": {"password": "selinal123", "role": "viewer", "email": "obed@epa.gov.gh"},
    "john": {"password": "john124", "role": "viewer", "email": "obed@epa.gov.gh"},
     "ludwick": {"password": "ludwick124", "role": "viewer", "email": "obed@epa.gov.gh"}
}

def login():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        st.title("🔐 Login to PM₂.₅ Monitoring App")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            user = USERS.get(username)
            if user and user["password"] == password:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.role = user["role"]
                st.session_state.user_email = user.get("email", f"{username}@epa.gov.gh")
                st.rerun()
            else:
                st.error("❌ Invalid credentials")

        st.stop()

def require_roles(*allowed_roles):
    if "role" not in st.session_state:
        st.error("❌ Please log in first.")
        st.stop()
    
    user_role = st.session_state.get("role")
    if user_role not in allowed_roles:
        st.error(f"❌ Your role ({user_role}) is not authorized to view this page.")
        st.stop()

def logout_button():
    if st.sidebar.button("🚪 Logout"):
        st.session_state.clear()
        st.rerun()

# === Data Utilities ===

def convert_timestamps_to_string(df):
    for col in df.select_dtypes(include=['datetime64[ns]']).columns:
        df[col] = df[col].dt.strftime('%Y-%m-%d %H:%M:%S')
    return df

def load_data_from_sheet(sheet):
    try:
        all_values = sheet.get_all_values()
        if not all_values:
            return pd.DataFrame()
        headers = all_values[0]
        rows = all_values[1:]
        if not rows:
            return pd.DataFrame(columns=headers)
        df = pd.DataFrame(rows, columns=headers)
        return convert_timestamps_to_string(df)
    except Exception as e:
        st.error(f"❌ Failed to load data from sheet: {e}")
        return pd.DataFrame()

def add_data(row):
    row.append(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    sheet.append_row(row)


def backup_deleted_row(row_data, sheet_name, row_number):
    """
    Backups a deleted row to a backup sheet.
    """
    backup_sheet = spreadsheet.worksheet("Deleted Records")
    from datetime import datetime

    # Optionally add timestamp and source row
    row_data.append(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    row_data.append(f"From row {row_number} in {sheet_name}")
    
    backup_sheet.append_row(row_data)


def delete_row(sheet, row_number):
    # row_data = sheet.row_values(row_number)
    # backup_deleted_row(row_data, "Main Sheet", row_number)
    sheet.delete_rows(row_number)


def delete_merged_record_by_index(index_to_delete):
    worksheet = sheet.spreadsheet.worksheet(MERGED_SHEET)
    row_data = worksheet.row_values(index_to_delete + 2)  # Skip header
    backup_deleted_row(row_data, "Merged Sheet", index_to_delete + 2)
    worksheet.delete_rows(index_to_delete + 2)

def undo_last_delete(sheet):
    st.warning("⚠️ Undo not supported. Check backup sheet manually.")



def merge_start_stop(df):
    start_df = df[df["Entry Type"] == "START"].copy()
    stop_df = df[df["Entry Type"] == "STOP"].copy()
    merge_keys = ["ID", "Site"]
    
    # Rename columns for merging
    start_df = start_df.rename(columns=lambda x: f"{x}_Start" if x not in merge_keys else x)
    stop_df = stop_df.rename(columns=lambda x: f"{x}_Stop" if x not in merge_keys else x)
    
    merged = pd.merge(start_df, stop_df, on=merge_keys, how="inner")

    # Compute Elapsed Time difference in seconds
    if "Elapsed Time (min)_Start" in merged and "Elapsed Time (min)_Stop" in merged:
        merged["Elapsed Time (min)_Start"] = pd.to_numeric(merged["Elapsed Time (min)_Start"], errors="coerce")
        merged["Elapsed Time (min)_Stop"] = pd.to_numeric(merged["Elapsed Time (min)_Stop"], errors="coerce")
        merged["Elapsed Time Diff (min)"] = (
            merged["Elapsed Time (min)_Stop"] - merged["Elapsed Time (min)_Start"]
        ) * 60

    # Compute Average Flow Rate
    if " Flow Rate (L/min)_Start" in merged and " Flow Rate (L/min)_Stop" in merged:
        merged[" Flow Rate (L/min)_Start"] = pd.to_numeric(merged[" Flow Rate (L/min)_Start"], errors="coerce")
        merged[" Flow Rate (L/min)_Stop"] = pd.to_numeric(merged[" Flow Rate (L/min)_Stop"], errors="coerce")
        merged["Average Flow Rate (L/min)"] = (
            merged[" Flow Rate (L/min)_Start"] + merged[" Flow Rate (L/min)_Stop"]
        ) / 2

    # Define desired column order
    desired_order = [
        "ID", "Site",
        "Entry Type_Start", "Monitoring Officer_Start", "Driver_Start", "Date _Start", "Time_Start",
        "Temperature (°C)_Start", " RH (%)_Start", "Pressure (mbar)_Start", "Weather _Start",
        "Wind Speed_Start", "Wind Direction_Start", "Elapsed Time (min)_Start", " Flow Rate (L/min)_Start",
        "Observation_Start", "Submitted At_Start",
        "Entry Type_Stop", "Monitoring Officer_Stop", "Driver_Stop", "Date _Stop", "Time_Stop",
        "Temperature (°C)_Stop", " RH (%)_Stop", "Pressure (mbar)_Stop", "Weather _Stop",
        "Wind Speed_Stop", "Wind Direction_Stop", "Elapsed Time (min)_Stop", " Flow Rate (L/min)_Stop",
        "Observation_Stop", "Submitted At_Stop",
        "Elapsed Time Diff (min)", "Average Flow Rate (L/min)"
    ]

    # Return only the columns that exist in the merged DataFrame in the specified order
    existing_cols = [col for col in desired_order if col in merged.columns]
    return merged[existing_cols]



def save_merged_data_to_sheet(df, spreadsheet, sheet_name):
    df = convert_timestamps_to_string(df)
    if sheet_name in [ws.title for ws in spreadsheet.worksheets()]:
        spreadsheet.del_worksheet(spreadsheet.worksheet(sheet_name))
    new_sheet = spreadsheet.add_worksheet(title=sheet_name, rows="1000", cols="50")
    new_sheet.update([df.columns.tolist()] + df.values.tolist())

def filter_dataframe(df, site_filter=None, date_range=None):
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

# === Display and Merge ===

def display_and_merge_data(df, spreadsheet, merged_sheet_name):
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
        st.success("✅ Merged records saved to Google Sheets.")
        st.dataframe(merged_df, use_container_width=True)
    else:
        st.warning("⚠️ No matching START and STOP records found to merge.")
