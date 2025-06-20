import streamlit as st
import pandas as pd
import gspread
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials
from gspread.exceptions import APIError, WorksheetNotFound
import json
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
    except WorksheetNotFound:
        sheet = spreadsheet.add_worksheet(title=sheet_name, rows="100", cols="20")

    if not sheet.get_all_values():
        sheet.append_row([
            "Entry Type", "Sector", "Company", "Region", "City", "Sampling Point",
            "Sampling Point Description", "Longitude", "Latitude", "Pollutant" "Monitoring Officer", "Driver",
            "Date", "Time", "Temperature (°C)", "RH (%)", "Pressure (mbar)",
            "Weather", "Wind Speed", "Wind Direction", "Elapsed Time (min)", "Flow Rate (L/min)", "Observation",
            "Submitted At"
        ])
    return sheet

sheet = ensure_main_sheet_initialized(spreadsheet, MAIN_SHEET)


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
    except APIError as e:
        st.error(f"❌ APIError: {e.response.status_code} - {e.response.reason}")
        st.text(f"Details: {e.response.text}")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"❌ Unexpected error: {e}")
        return pd.DataFrame()


def add_data(row, username):
    row.append(username)
    row.append(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    sheet.append_row(row)


def merge_start_stop(df):
    df.columns = df.columns.str.strip()
    merge_keys = ["Sector", "Company"]

    start_df = df[df["Entry Type"] == "START"].copy()
    stop_df = df[df["Entry Type"] == "STOP"].copy()

    if start_df.empty or stop_df.empty:
        return pd.DataFrame()

    start_df = start_df.reset_index(drop=True)
    stop_df = stop_df.reset_index(drop=True)

    start_df["seq"] = start_df.groupby(merge_keys).cumcount() + 1
    stop_df["seq"] = stop_df.groupby(merge_keys).cumcount() + 1

    start_df = start_df.rename(columns=lambda x: f"{x}_Start" if x not in merge_keys + ["seq"] else x)
    stop_df = stop_df.rename(columns=lambda x: f"{x}_Stop" if x not in merge_keys + ["seq"] else x)

    merged = pd.merge(start_df, stop_df, on=merge_keys + ["seq"], how="inner")

    if "Elapsed Time (min)_Start" in merged.columns and "Elapsed Time (min)_Stop" in merged.columns:
        merged["Elapsed Time (min)_Start"] = pd.to_numeric(merged["Elapsed Time (min)_Start"], errors="coerce")
        merged["Elapsed Time (min)_Stop"] = pd.to_numeric(merged["Elapsed Time (min)_Stop"], errors="coerce")
        merged["Elapsed Time Diff (min)"] = (
            merged["Elapsed Time (min)_Stop"] - merged["Elapsed Time (min)_Start"]
        ) * 60

    flow_start_col = "Flow Rate (L/min)_Start"
    flow_stop_col = "Flow Rate (L/min)_Stop"
    if flow_start_col in merged.columns and flow_stop_col in merged.columns:
        merged[flow_start_col] = pd.to_numeric(merged[flow_start_col], errors="coerce")
        merged[flow_stop_col] = pd.to_numeric(merged[flow_stop_col], errors="coerce")
        merged["Average Flow Rate (L/min)"] = (merged[flow_start_col] + merged[flow_stop_col]) / 2

    merged = merged.drop(columns=["seq"])

    desired_order = [
        "Sector", "Company",
        "Entry Type_Start", "Sampling Point_Start", "Sampling Point Description", "Longitude", "Latitude","Pollutant",
        "Monitoring Officer_Start", "Driver_Start", "Date_Start", "Time_Start",
        "Temperature (°C)_Start", "RH (%)_Start", "Pressure (mbar)_Start", "Weather_Start",
        "Wind Speed_Start", "Wind Direction_Start", "Elapsed Time (min)_Start", "Flow Rate (L/min)_Start",
        "Observation_Start", "Submitted At_Start",
        "Entry Type_Stop", "Sampling Point_Start","Monitoring Officer_Stop", "Driver_Stop", "Date_Stop", "Time_Stop",
        "Temperature (°C)_Stop", "RH (%)_Stop", "Pressure (mbar)_Stop", "Weather_Stop",
        "Wind Speed_Stop", "Wind Direction_Stop", "Elapsed Time (min)_Stop", "Flow Rate (L/min)_Stop",
        "Observation_Stop", "Submitted At_Stop",
        "Elapsed Time Diff (min)", "Average Flow Rate (L/min)"
    ]

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
        df = df[df["Company"] == site_filter]
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
        site_filter = st.selectbox("Filter by Company", ["All"] + sorted(df["Company"].dropna().unique()))
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
