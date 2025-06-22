import streamlit as st
import pandas as pd
import gspread
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials
from gspread.exceptions import APIError, WorksheetNotFound

from constants import SPREADSHEET_ID, MAIN_SHEET, MERGED_SHEET, CALC_SHEET

# === Google Sheets Setup ===
creds_dict = st.secrets["GOOGLE_CREDENTIALS"]  # Already a dictionary; no json.loads needed

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
            "Sampling Point Description", "Longitude", "Latitude", "Pollutant", "Monitoring Officer", "Driver",
            "Date Time", "Temperature (°C)", "RH (%)", "Pressure (mbar)",
            "Weather", "Wind Speed", "Wind Direction", "Elapsed Time (min)", "Flow Rate (L/min)", "Observation", "Submitted By",
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
    import pandas as pd  # Ensure pandas is available if not globally imported

    # Clean column names (remove leading/trailing spaces)
    df.columns = df.columns.str.strip()

    # Define keys for grouping and merging
    merge_keys = ["Sector", "Company"]

    # Split data into START and STOP entries
    start_df = df[df["Entry Type"] == "START"].copy()
    stop_df = df[df["Entry Type"] == "STOP"].copy()

    # Debug info (optional)
    st.write(f"🟢 Found {len(start_df)} START records")
    st.write(f"🔴 Found {len(stop_df)} STOP records")

    if start_df.empty or stop_df.empty:
        return pd.DataFrame()

    # Add sequence numbers to match START/STOP by order
    start_df["seq"] = start_df.groupby(merge_keys).cumcount() + 1
    stop_df["seq"] = stop_df.groupby(merge_keys).cumcount() + 1

    # Rename columns to indicate source (START or STOP), except merge keys and sequence
    start_df = start_df.rename(columns=lambda x: f"{x}_Start" if x not in merge_keys + ["seq"] else x)
    stop_df = stop_df.rename(columns=lambda x: f"{x}_Stop" if x not in merge_keys + ["seq"] else x)

    # Merge START and STOP data on merge keys + sequence number
    merged = pd.merge(start_df, stop_df, on=merge_keys + ["seq"], how="inner")

    # Convert numeric fields before calculating
    if "Elapsed Time (min)_Start" in merged.columns and "Elapsed Time (min)_Stop" in merged.columns:
        merged["Elapsed Time (min)_Start"] = pd.to_numeric(merged["Elapsed Time (min)_Start"], errors="coerce")
        merged["Elapsed Time (min)_Stop"] = pd.to_numeric(merged["Elapsed Time (min)_Stop"], errors="coerce")
        merged["Elapsed Time Diff (min)"] = (
            merged["Elapsed Time (min)_Stop"] - merged["Elapsed Time (min)_Start"]
        ) * 60  # Convert to seconds

    if "Flow Rate (L/min)_Start" in merged.columns and "Flow Rate (L/min)_Stop" in merged.columns:
        merged["Flow Rate (L/min)_Start"] = pd.to_numeric(merged["Flow Rate (L/min)_Start"], errors="coerce")
        merged["Flow Rate (L/min)_Stop"] = pd.to_numeric(merged["Flow Rate (L/min)_Stop"], errors="coerce")
        merged["Average Flow Rate (L/min)"] = (
            merged["Flow Rate (L/min)_Start"] + merged["Flow Rate (L/min)_Stop"]
        ) / 2

    # Drop the sequence column
    merged = merged.drop(columns=["seq"])

    # Define preferred column order (if available)
    desired_order = [
        "Sector", "Company",
        "Entry Type_Start", "Sampling Point_Start", "Sampling Point Description_Start",
        "Longitude_Start", "Latitude_Start", "Pollutant_Start", "Monitoring Officer_Start",
        "Driver_Start", "Date Time_Start", "Temperature (°C)_Start", "RH (%)_Start",
        "Pressure (mbar)_Start", "Weather_Start", "Wind Speed_Start", "Wind Direction_Start",
        "Elapsed Time (min)_Start", "Flow Rate (L/min)_Start", "Observation_Start", "Submitted At_Start",

        "Entry Type_Stop", "Sampling Point_Stop", "Monitoring Officer_Stop", "Driver_Stop",
        "Date Time_Stop", "Temperature (°C)_Stop", "RH (%)_Stop", "Pressure (mbar)_Stop",
        "Weather_Stop", "Wind Speed_Stop", "Wind Direction_Stop", "Elapsed Time (min)_Stop",
        "Flow Rate (L/min)_Stop", "Observation_Stop", "Submitted At_Stop",

        "Elapsed Time Diff (min)", "Average Flow Rate (L/min)"
    ]

    # Only use columns that exist
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

def display_and_merge_data(df, spreadsheet, merged_sheet_name):
    st.subheader("📊 Debug Info")

    # Raw data overview
    st.write("📁 Raw DataFrame shape:", df.shape)
    st.dataframe(df.head(), use_container_width=True)

    if df.empty:
        st.info("ℹ️ No data submitted yet.")
        return

    # Optional filters
    with st.expander("🔍 Filter Records"):
        site_filter = st.selectbox("Filter by Company", ["All"] + sorted(df["Company"].dropna().unique()))
        date_range = st.date_input("Filter by Date Range", [])

    # Apply filters
    filtered_df = filter_dataframe(df, site_filter, date_range)
    st.write("📁 Filtered DataFrame shape:", filtered_df.shape)
    st.dataframe(filtered_df.head(), use_container_width=True)

    # Breakdown of START and STOP entries
    start_df = filtered_df[filtered_df["Entry Type"] == "START"]
    stop_df = filtered_df[filtered_df["Entry Type"] == "STOP"]
    st.write(f"🟢 START entries: {len(start_df)}")
    st.write(f"🔴 STOP entries: {len(stop_df)}")

    # Proceed to merging
    merged_df = merge_start_stop(filtered_df)
    st.write("📦 Merged DataFrame shape:", merged_df.shape)

    if not merged_df.empty:
        # Save to sheet
        save_merged_data_to_sheet(merged_df, spreadsheet, merged_sheet_name)
        st.success("✅ Merged records saved to Google Sheets.")
        st.dataframe(merged_df, use_container_width=True)
    else:
        st.warning("⚠️ No matching START and STOP records found to merge.")
