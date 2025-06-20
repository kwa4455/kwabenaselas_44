import streamlit as st
from datetime import datetime
from gsheets import init_gsheet_client, open_worksheet, append_data_to_sheet
from general import general_info_form
from forms_monitoring import monitoring_type_form
from modules.authentication import require_role


def show():
    require_role(["admin", "officer"])

# Initialize Google Sheets client
client = init_gsheet_client()


# Step 1: General Info Form
general_data = general_info_form()

# Step 2: Monitoring Form (Noise, Gases, Stack Emission, VOCs)
monitoring_type, monitoring_data = monitoring_type_form()

# Submit Button
if st.button("Submit Entry"):
    if not username:
        st.error("Please enter your name before submitting.")
    else:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Common data from general_info_form
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
        ]

        # Add submission info
        common_data.append(username)      # Submitted by
        common_data.append(timestamp)     # Submitted at

        # Handle submission by monitoring type
        try:
            if monitoring_type == "Noise":
                worksheet = open_worksheet(client, "Noise")
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
                worksheet = open_worksheet(client, "Gases")
                gases_data = [
                    monitoring_data.get("no2", ""),
                    monitoring_data.get("so2", ""),
                ]
                append_data_to_sheet(worksheet, common_data + gases_data)
                st.success("Gases data saved successfully!")

            elif monitoring_type == "Stack Emission":
                worksheet = open_worksheet(client, "Stack Emission")
                stack_data = [
                    monitoring_data.get("gen_set", ""),
                    monitoring_data.get("installation", ""),
                    monitoring_data.get("fuel", ""),
                    monitoring_data.get("measurement_result", ""),
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
                worksheet = open_worksheet(client, "VOCs")
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
