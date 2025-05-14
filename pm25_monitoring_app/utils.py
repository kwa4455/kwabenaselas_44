import streamlit as st
import pandas as pd
import gspread
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials
import json
import time
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
    return client.open_by_key(st.secrets["SPREADSHEET_ID"])

spreadsheet = setup_google_sheets()

# Try to get the main sheet, if it doesn't exist create one
try:
    sheet = spreadsheet.worksheet(st.secrets["MAIN_SHEET"])
except gspread.WorksheetNotFound:
    sheet = spreadsheet.add_worksheet(title=st.secrets["MAIN_SHEET"], rows="100", cols="20")
    sheet.append_row([
        "Entry Type", "ID", "Site", "Monitoring Officer", "Driver",
        "Date", "Time", "Temperature (°C)", "RH (%)", "Pressure (mbar)",
        "Weather", "Wind", "Elapsed Time (min)", "Flow Rate (L/min)", "Observation",
        "Submitted At"
    ])

# === Authentication ===
# Store the list of users and their roles
users = {
    "admin": {"email": "admin@example.com", "password": "admin123", "role": "admin"},
    "editor": {"email": "editor@example.com", "password": "editor123", "role": "editor"},
    "collector": {"email": "collector@example.com", "password": "collector123", "role": "collector"}
}

# === Login Function ===
def login():
    st.title("Login")
    email = st.text_input("Email", "")
    password = st.text_input("Password", "", type="password")

    if st.button("Log in"):
        user = authenticate_user(email, password)
        if user:
            st.session_state["user_email"] = user["email"]
            st.session_state["role"] = user["role"]
            st.success(f"Logged in successfully as {user['role']}")
            st.experimental_rerun()  # Refresh the app to load the authenticated user's data
        else:
            st.error("Invalid email or password")

# === Authenticate User ===
def authenticate_user(email, password):
    for user, credentials in users.items():
        if credentials["email"] == email and credentials["password"] == password:
            return credentials
    return None

# === Role-based Access Control ===
def require_roles(*allowed_roles):
    if "role" not in st.session_state:
        st.error("You are not logged in. Please log in first.")
        st.stop()

    user_role = st.session_state["role"]
    if user_role not in allowed_roles:
        st.error(f"Access denied. You need one of these roles: {', '.join(allowed_roles)}.")
        st.stop()

# === Logout Button ===
def logout_button():
    if st.button("Logout"):
        st.session_state.clear()
        st.experimental_rerun()

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

# === Main App Logic ===
def main():
    if "user_email" not in st.session_state:
        login()  # Show the login form if the user is not logged in
    else:
        st.title(f"Welcome, {st.session_state['user_email']}!")
        st.write(f"Role: {st.session_state['role']}")
        
        # Example of restricting access to certain roles
        require_roles("admin")  # Only allow admins to access this page
        st.write("This content is for admins only!")

        # Load the data from Google Sheets and display it
        df = load_data_from_sheet(sheet)
        display_and_merge_data(df, spreadsheet, "Merged_Data")

        # Show a logout button
        logout_button()

if __name__ == "__main__":
    main()
