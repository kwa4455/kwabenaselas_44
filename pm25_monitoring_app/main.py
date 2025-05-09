import streamlit as st
from utils import load_data_from_sheet, add_data, merge_start_stop,save_merged_data_to_sheet,sheet,spreadsheet
from constants import SPREADSHEET_ID, MAIN_SHEET,MERGED_SHEET

st.set_page_config(page_title="PM2.5 Monitoring App", layout="wide")
st.title("🌫️ PM2.5 Monitoring Dashboard")

st.markdown("""
Welcome to the PM2.5 Air Quality Monitoring Dashboard. Use the sidebar to navigate between:
- 📝 New data entry
- ✏️ Edit submitted records
- 📊 Analysis and reports
""")

if "df" not in st.session_state:
    sheet = spreadsheet.worksheet(MAIN_SHEET)
    spreadsheet = client.open_by_key(SPREADSHEET_ID)
    df = load_data_from_sheet(sheet)
    st.session_state.df = df
    st.session_state.sheet = sheet
    st.session_state.spreadsheet = spreadsheet
