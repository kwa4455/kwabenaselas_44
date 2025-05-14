import streamlit as st
import pandas as pd
import gspread
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials
from google_auth_oauthlib.flow import Flow
import requests
import json
from constants import SPREADSHEET_ID, MAIN_SHEET, MERGED_SHEET


# Authenticate with Google Sheets API
def authenticate_google_sheets():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("path/to/your/service_account.json", scope)
    client = gspread.authorize(creds)
    return client


# === Google Sheets Setup ===
def setup_google_sheets():
    creds_json = st.secrets["GOOGLE_CREDENTIALS"]
    creds_dict = json.loads(creds_json)
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    return client.open_by_key(SPREADSHEET_ID)

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

    start_df = start_df.rename(columns=lambda x: f"{x}_Start" if x not in merge_keys else x)
    stop_df = stop_df.rename(columns=lambda x: f"{x}_Stop" if x not in merge_keys else x)

    merged = pd.merge(start_df, stop_df, on=merge_keys, how="inner")

    if "Elapsed Time (min)_Start" in merged.columns and "Elapsed Time (min)_Stop" in merged.columns:
        merged["Elapsed Time Diff (min)"] = (
            merged["Elapsed Time (min)_Stop"] - merged["Elapsed Time (min)_Start"]
        )

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

def delete_row(sheet, row_number):
    sheet.delete_rows(row_number)

def delete_merged_record_by_index(spreadsheet, sheet_name, row_number):
    sheet = spreadsheet.worksheet(sheet_name)
    sheet.delete_rows(row_number)

import time

# Store a backup of the deleted record temporarily
deleted_records = []

def delete_row(sheet, row_number, record_data=None):
    """Delete a row but back it up for potential undo."""
    if record_data:
        # Save record to the deleted records list (backup)
        deleted_records.append({"time": time.time(), "data": record_data})
    try:
        sheet.delete_row(row_number)
    except Exception as e:
        print(f"Error deleting row {row_number}: {e}")

def undo_last_delete(sheet):
    """Undo the last delete action."""
    if deleted_records:
        last_deleted = deleted_records.pop()
        # You can now re-insert the deleted record if needed.
        sheet.append_row(last_deleted["data"])  # You may need to adjust the format of data.
        print(f"Restored record: {last_deleted}")

# === Google OAuth Authentication ===

def authenticate_with_google():
    client_config = {
        "web": {
            "client_id": st.secrets["google_client_secrets"]["client_id"],
            "project_id": st.secrets["google_client_secrets"]["project_id"],
            "auth_uri": st.secrets["google_client_secrets"]["auth_uri"],
            "token_uri": st.secrets["google_client_secrets"]["token_uri"],
            "auth_provider_x509_cert_url": st.secrets["google_client_secrets"]["auth_provider_x509_cert_url"],
            "client_secret": st.secrets["google_client_secrets"]["client_secret"],
            "redirect_uris": [st.secrets["google_client_secrets"]["redirect_uri"]]
        }
    }

    redirect_uri = client_config["web"]["redirect_uris"][0]

    flow = Flow.from_client_config(
        client_config=client_config,
        scopes=["openid", "https://www.googleapis.com/auth/userinfo.email"],
        redirect_uri=redirect_uri
    )

    if "code" not in st.query_params:
        auth_url, _ = flow.authorization_url(prompt="consent")
        st.markdown(f"[🔐 Sign in with Google]({auth_url})")
        st.stop()
    else:
        flow.fetch_token(code=st.query_params["code"])
        session = flow.authorized_session()
        user_info = session.get("https://www.googleapis.com/userinfo/v2/me").json()
        email = user_info["email"]

        st.session_state["user_email"] = email

        for role, emails in st.secrets["roles"].items():
            if email in emails:
                st.session_state["role"] = role
                return email, role

        st.error("You are not assigned a role. Access denied.")
        st.stop()

def require_roles(*allowed_roles):
    if "role" not in st.session_state:
        st.warning("Unauthorized access.")
        st.stop()
    if st.session_state["role"] not in allowed_roles:
        st.warning("You do not have permission to view this page.")
        st.stop()

def logout_button():
    if st.sidebar.button("🚪 Logout"):
        st.session_state.clear()
        st.experimental_rerun()


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
