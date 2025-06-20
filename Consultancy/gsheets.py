import gspread
from oauth2client.service_account import ServiceAccountCredentials
import streamlit as st


@st.cache_resource
def init_gsheet_client():
    creds_dict = st.secrets["GOOGLE_CREDENTIALS"]
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive.file",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    return client

def open_worksheet(client, sheet_name):
    spreadsheet = client.open_by_key(SPREADSHEET_ID)
    try:
        worksheet = spreadsheet.worksheet(sheet_name)
    except gspread.WorksheetNotFound:
        worksheet = spreadsheet.add_worksheet(title=sheet_name, rows="1000", cols="20")
    return worksheet

def append_data_to_sheet(worksheet, data_list):
    worksheet.append_row(data_list, value_input_option='USER_ENTERED')
