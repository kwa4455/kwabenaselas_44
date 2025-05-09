import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
from constants import SPREADSHEET_ID, MAIN_SHEET  # ✅ Add this line

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

# === Functions ===
def load_data_from_sheet(sheet):
    data = sheet.get_all_records()
    df = pd.DataFrame(data)
    df["Submitted At"] = pd.to_datetime(df["Submitted At"])
    df["Date"] = pd.to_datetime(df["Date"])
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
    if sheet_name in [ws.title for ws in spreadsheet.worksheets()]:
        sheet = spreadsheet.worksheet(sheet_name)
        spreadsheet.del_worksheet(sheet)
    sheet = spreadsheet.add_worksheet(title=sheet_name, rows="1000", cols="50")
    sheet.update([df.columns.tolist()] + df.values.tolist())



