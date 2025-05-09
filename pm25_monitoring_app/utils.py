import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
from constants import SPREADSHEET_ID, MAIN_SHEET,MERGED_SHEET  # ✅ Add this line

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

# Ensure Observations worksheet exists
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

def convert_timestamps_to_string(df):
    """Convert all Timestamp columns in a DataFrame to string."""
    for column in df.select_dtypes(include=['datetime64[ns]']).columns:
        df[column] = df[column].dt.strftime('%Y-%m-%d %H:%M:%S')  # Convert to string format
    return df

def load_data_from_sheet(sheet):
    data = sheet.get_all_records()
    df = pd.DataFrame(data)
    
    # Convert datetime columns to string
    df = convert_timestamps_to_string(df)

    return df


def add_data(row):
    row.append(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))  # Timestamp
    sheet.append_row(row)

def merge_start_stop(df):
    # Separate START and STOP records
    start_df = df[df["Entry Type"] == "START"].copy()
    stop_df = df[df["Entry Type"] == "STOP"].copy()

    # Ensure common key for merging (e.g., ID and Site)
    merge_keys = ["ID", "Site"]

    # Rename columns to distinguish between START and STOP
    start_df = start_df.rename(columns=lambda x: f"{x}_Start" if x not in merge_keys else x)
    stop_df = stop_df.rename(columns=lambda x: f"{x}_Stop" if x not in merge_keys else x)

    # Merge START and STOP records on ID and Site
    merged_df = pd.merge(start_df, stop_df, on=merge_keys, how="inner")

    # Calculate elapsed time difference if columns exist
    if "Elapsed Time (min)_Start" in merged_df.columns and "Elapsed Time (min)_Stop" in merged_df.columns:
        merged_df["Elapsed Time Diff (min)"] = (
            merged_df["Elapsed Time (min)_Stop"] - merged_df["Elapsed Time (min)_Start"]
        )

    return merged_df

def save_merged_data_to_sheet(df, spreadsheet, sheet_name):
    # Convert all Timestamp columns to strings before saving to the sheet
    df = convert_timestamps_to_string(df)

    if sheet_name in [ws.title for ws in spreadsheet.worksheets()]:
        sheet = spreadsheet.worksheet(sheet_name)
        spreadsheet.del_worksheet(sheet)

    sheet = spreadsheet.add_worksheet(title=sheet_name, rows="1000", cols="50")
    sheet.update([df.columns.tolist()] + df.values.tolist())


def filter_dataframe(df, site_filter=None, date_range=None):
    """Filter the dataframe by site and date range."""
    if df.empty:
        return df

    # Ensure datetime format
    if "Submitted At" in df.columns:
        df["Submitted At"] = pd.to_datetime(df["Submitted At"], errors="coerce")

    if site_filter and site_filter != "All":
        df = df[df["Site"] == site_filter]

    if date_range and len(date_range) == 2:
        start, end = date_range
        df = df[(df["Submitted At"].dt.date >= start) & (df["Submitted At"].dt.date <= end)]

    return df


def display_and_merge_data(df, spreadsheet, merged_sheet_name):
    """Display filtered data, merge START/STOP pairs, and save merged data."""
    import streamlit as st

    if df.empty:
        st.info("No data submitted yet.")
        return

    with st.expander("🔍 Filter Records"):
        site_filter = st.selectbox("Filter by Site", ["All"] + sorted(df["Site"].dropna().unique().tolist()))
        date_range = st.date_input("Filter by Date Range", [])

    filtered_df = filter_dataframe(df, site_filter, date_range)
    st.dataframe(filtered_df, use_container_width=True)

    merged_df = merge_start_stop(filtered_df)
    if not merged_df.empty:
        save_merged_data_to_sheet(merged_df, spreadsheet, sheet_name=merged_sheet_name)
        st.success("Merged records saved to Google Sheets.")
        st.dataframe(merged_df, use_container_width=True)
    else:
        st.warning("No matching START and STOP records found to merge.")



