import streamlit as st
import pandas as pd
import gspread
from datetime import datetime
from google.oauth2.service_account import Credentials
import json
import time
from constants import SPREADSHEET_ID, MAIN_SHEET, MERGED_SHEET,CALC_SHEET


scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
credentials = Credentials.from_service_account_info(creds_dict, scopes=scopes)
gc = gspread.authorize(credentials)

SPREADSHEET_ID = "your_spreadsheet_id_here"
spreadsheet = gc.open_by_key(SPREADSHEET_ID)
sheet = spreadsheet.sheet1

MAIN_SHEET = 'Observations'
MERGED_SHEET = 'Merged Records'
CALC_SHEET = "PM Calculations"


# Ensure Observations worksheet exists
try:
    sheet = spreadsheet.worksheet(MAIN_SHEET)
except gspread.WorksheetNotFound:
    sheet = spreadsheet.add_worksheet(title=MAIN_SHEET, rows="100", cols="20")
    
    sheet.append_row([
        "Entry Type", "ID", "Site", "Monitoring Officer", "Driver",
        "Date", "Time", "Temperature (°C)", "RH (%)", "Pressure (mbar)",
        "Weather", "Wind Speed", "Wind Direction", "Elapsed Time (min)", "Flow Rate (L/min)", "Observation",
        "Submitted At"
    ])
USERS = {
    "clement": {"password": "admin123", "role": "admin", "email": "clement@epa.gov.gh"},
    "peter": {"password": "editor123", "role": "editor", "email": "peter@epa.gov.gh"},
    "mawuli": {"password": "collector123", "role": "collector", "email": "mawuli@epa.gov.gh"},
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
                st.experimental_rerun()
            else:
                st.error("❌ Invalid credentials")

        st.stop()  # Prevent execution beyond login screen


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
        st.experimental_rerun()

def delete_row(sheet, row_number):
    """Deletes a row from the main sheet and saves a backup."""
    row_data = sheet.row_values(row_number)
    backup_deleted_row(row_data, "Main Sheet", row_number)
    sheet.delete_rows(row_number)

def delete_merged_record_by_index(index_to_delete):
    """Deletes a row from the merged sheet by index and saves a backup."""
    worksheet = sheet.spreadsheet.worksheet(MERGED_SHEET)
    row_data = worksheet.row_values(index_to_delete + 2)  # +2 to skip header
    backup_deleted_row(row_data, "Merged Sheet", index_to_delete + 2)
    worksheet.delete_rows(index_to_delete + 2)

def undo_last_delete(sheet):
    """Cannot restore automatically with backup sheet. Just inform user."""
    st.warning("⚠️ Undo not supported with backup sheet. Check 'Deleted Records Backup' for recovery.")


# === Data Utilities ===
def convert_timestamps_to_string(df):
    for col in df.select_dtypes(include=['datetime64[ns]']).columns:
        df[col] = df[col].dt.strftime('%Y-%m-%d %H:%M:%S')
    return df

def load_data_from_sheet(sheet):
    data = sheet.get_all_records()
    df = pd.DataFrame(data)
    return convert_timestamps_to_string(df)

def add_data(row):
    row.append(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    sheet.append_row(row)

def merge_start_stop(df):
    start_df = df[df["Entry Type"] == "START"].copy()
    stop_df = df[df["Entry Type"] == "STOP"].copy()
    merge_keys = ["ID", "Site"]

    # Rename columns to distinguish start/stop
    start_df = start_df.rename(columns=lambda x: f"{x}_Start" if x not in merge_keys else x)
    stop_df = stop_df.rename(columns=lambda x: f"{x}_Stop" if x not in merge_keys else x)

    # Merge the two datasets
    merged = pd.merge(start_df, stop_df, on=merge_keys, how="inner")

    # Compute elapsed time difference if available
    if "Elapsed Time (min)_Start" in merged.columns and "Elapsed Time (min)_Stop" in merged.columns:
        merged["Elapsed Time Diff (min)"] = (
            merged["Elapsed Time (min)_Stop"] - merged["Elapsed Time (min)_Start"]
        )

    # Compute average flow rate if available
    if "Flow Rate (L/min)_Start" in merged.columns and "Flow Rate (L/min)_Stop" in merged.columns:
        merged["Average Flow Rate (L/min)"] = (
            merged["Flow Rate (L/min)_Start"] + merged["Flow Rate (L/min)_Stop"]
        ) / 2

    # Optional: Reorder columns to highlight key info
    wind_columns = [
        "Wind Speed_Start", "Wind Direction_Start",
        "Wind Speed_Stop", "Wind Direction_Stop"
    ]
    existing_wind_columns = [col for col in wind_columns if col in merged.columns]

    front_cols = ["ID", "Site"]
    calculated_cols = ["Elapsed Time Diff (min)", "Average Flow Rate (L/min)"]
    existing_calc_cols = [col for col in calculated_cols if col in merged.columns]

    other_cols = [
        col for col in merged.columns
        if col not in front_cols + existing_wind_columns + existing_calc_cols
    ]

    merged = merged[front_cols + existing_wind_columns + existing_calc_cols + other_cols]

    return merged


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

# === UI Utility ===

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
        st.success("Merged records saved to Google Sheets.")
        st.dataframe(merged_df, use_container_width=True)
    else:
        st.warning("No matching START and STOP records found to merge.")

