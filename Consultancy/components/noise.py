import streamlit as st
import gspread
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials
from general import general_info_form
from forms_monitoring import monitoring_type_form
from modules.authentication import require_role
from constants import (
    SPREADSHEET_ID,
    NOISE_SHEET_NAME,
    GASES_SHEET_NAME,
    STACK_SHEET_NAME,
    VOC_SHEET_NAME
)

# === Google Sheets Setup ===
creds_dict = st.secrets["GOOGLE_CREDENTIALS"]  # Already a dictionary

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
]
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)

def open_worksheet(client, sheet_name):
    spreadsheet = client.open_by_key(SPREADSHEET_ID)
    try:
        worksheet = spreadsheet.worksheet(sheet_name)
    except gspread.WorksheetNotFound:
        worksheet = spreadsheet.add_worksheet(title=sheet_name, rows="1000", cols="20")
    return worksheet

def append_data_to_sheet(worksheet, data_list):
    worksheet.append_row(data_list, value_input_option='USER_ENTERED')

# === Main App Function ===
def show():
    require_role(["admin", "officer"])

    st.title("Environmental Monitoring Form")

    # Step 1: General Info Form
    general_data = general_info_form()

    # Step 2: Monitoring Form
    monitoring_type, monitoring_data = monitoring_type_form()

    # Get username input
    username = st.text_input("Your Name")

    # Submit Button
    if st.button("Submit Entry"):
        if not username:
            st.error("Please enter your name before submitting.")
        else:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            common_data = [
                timestamp,
                general_data.get("sector", ""),
                general_data.get("company", ""),
                general_data.get("region", ""),
                general_data.get("city", ""),
                general_data.get("sampling_point_name", ""),
                general_data.get("coordinate", ""),
                general_data.get("description", ""),
                general_data.get("date_time").strftime("%Y-%m-%d %H:%M:%S") if general_data.get("date_time") else "",
                general_data.get("weather", ""),
                general_data.get("temperature", ""),
                general_data.get("wind_speed", ""),
                general_data.get("wind_direction", ""),
                general_data.get("humidity", ""),
                ", ".join(general_data.get("selected_officers", [])),
                general_data.get("driver", ""),
                username,
                timestamp,
            ]

            try:
                if monitoring_type == "Noise":
                    worksheet = open_worksheet(client, NOISE_SHEET_NAME)
                    noise_data = [
                        monitoring_data.get("leq", ""),
                        monitoring_data.get("l10", ""),
                        monitoring_data.get("l50", ""),
                        monitoring_data.get("l90", ""),
                        monitoring_data.get("lmax", ""),
                    ]
                    append_data_to_sheet(worksheet, common_data + noise_data)
                    st.success("Noise data saved successfully!")

                elif monitoring_type == "Gases":
                    worksheet = open_worksheet(client, GASES_SHEET_NAME)
                    gases_data = [
                        monitoring_data.get("no2", ""),
                        monitoring_data.get("so2", ""),
                    ]
                    append_data_to_sheet(worksheet, common_data + gases_data)
                    st.success("Gases data saved successfully!")

                elif monitoring_type == "Stack Emission":
                    worksheet = open_worksheet(client, STACK_SHEET_NAME)
                    stack_data = [
                        monitoring_data.get("gen_set", ""),
                        monitoring_data.get("installation", ""),
                        monitoring_data.get("fuel", ""),
                        monitoring_data.get("t_room", ""),
                        monitoring_data.get("t_gas", ""),
                        monitoring_data.get("co2", ""),
                        monitoring_data.get("o2", ""),
                        monitoring_data.get("co", ""),
                        monitoring_data.get("so2_stack", ""),
                        monitoring_data.get("no2_stack", ""),
                    ]
                    append_data_to_sheet(worksheet, common_data + stack_data)
                    st.success("Stack Emission data saved successfully!")

                elif monitoring_type == "VOCs":
                    worksheet = open_worksheet(client, VOC_SHEET_NAME)
                    voc_data = [
                        monitoring_data.get("voc_total", ""),
                        monitoring_data.get("benzene", ""),
                        monitoring_data.get("toluene", ""),
                        monitoring_data.get("xylene", ""),
                    ]
                    append_data_to_sheet(worksheet, common_data + voc_data)
                    st.success("VOCs data saved successfully!")

                else:
                    st.warning("Please select a valid monitoring type before submitting.")

            except Exception as e:
                st.error(f"Failed to save data: {e}")
