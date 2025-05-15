import streamlit as st
import pandas as pd
from datetime import datetime
from utils import require_roles, spreadsheet
from constants import MERGED_SHEET,CALC_SHEET

st.title("✏️ PM Calculator")

st.info("Welcome to the PM Calculator form. Please provide monitoring details below.")
# Auth Check
require_roles("admin", "editor", "collector")

# Load merged records data
try:
    merged_data = spreadsheet.worksheet(MERGED_SHEET).get_all_records()
    df_merged = pd.DataFrame(merged_data)
    site_ids = df_merged["ID"].dropna().unique().tolist()
    site_names = df_merged["Site"].dropna().unique().tolist()
    officer_names = df_merged["Officer"].dropna().unique().tolist()
except Exception as e:
    st.error("Failed to load merged records data.")
    site_ids = []
    site_names = []
    officer_names = []

# Page Title
st.title("🧮 PM₂.₅ Concentration Calculation Tool")
st.markdown("Enter sample data to calculate PM₂.₅ concentrations in µg/m³.")

# Table Form Setup
rows = st.number_input("Number of entries", min_value=1, max_value=50, value=5)

default_data = {
    "Date": [datetime.today().date()] * rows,
    "Site ID": [""] * rows,
    "Site": [""] * rows,
    "Officer(s)": [""] * rows,
    "Elapsed Time (min)": [1200] * rows,
    "Flow Rate (L/min)": [5.0] * rows,
    "Pre Weight (mg)": [0.0] * rows,
    "Post Weight (mg)": [0.0] * rows
}

df_input = pd.DataFrame(default_data)

edited_df = st.data_editor(
    df_input,
    num_rows="dynamic",
    key="pm_table",
    use_container_width=True,
    column_config={
        "Site ID": st.column_config.SelectboxColumn("Site ID", options=site_ids),
        "Site": st.column_config.SelectboxColumn("Site", options=site_names),
        "Date": st.column_config.DateColumn("Date")
    }
)

# Calculation Logic
def calculate_pm(row):
    try:
        elapsed = float(row["Elapsed Time (min)"])
        flow = float(row["Flow Rate (L/min)"])
        pre = float(row["Pre Weight (mg)"])
        post = float(row["Post Weight (mg)"])
        mass = post - pre  # in mg
        if elapsed < 1200:
            return "Elapsed < 1200"
        conc = (mass / (elapsed * flow)) * 1_000_000  # mg -> µg/m³
        return round(conc, 2)
    except:
        return "Error"

# Auto-Calculate PM
edited_df["PM₂.₅ (µg/m³)"] = edited_df.apply(calculate_pm, axis=1)

column_config={
    "Site ID": st.column_config.SelectboxColumn("Site ID", options=site_ids, help="Select from loaded IDs"),
    "Site": st.column_config.SelectboxColumn("Site", options=site_names, help="Select the monitoring site"),
    "Date": st.column_config.DateColumn("Date"),
    "Elapsed Time (min)": st.column_config.NumberColumn("Elapsed Time (min)", help="Must be ≥ 1200 for valid results"),
    "Flow Rate (L/min)": st.column_config.NumberColumn("Flow Rate (L/min)", help="Should be > 0"),
    "Pre Weight (mg)": st.column_config.NumberColumn("Pre Weight (mg)", help="Initial filter mass"),
    "Post Weight (mg)": st.column_config.NumberColumn("Post Weight (mg)", help="Mass after sampling")
}


# Display Calculated Data
st.subheader("Calculated Results")
st.dataframe(edited_df, use_container_width=True)

if st.button("✅ Save Valid Entries"):
    valid_rows = []
    errors = []

    for idx, row in edited_df.iterrows():
        try:
            elapsed = float(row["Elapsed Time (min)"])
            flow = float(row["Flow Rate (L/min)"])
            pre = float(row["Pre Weight (mg)"])
            post = float(row["Post Weight (mg)"])
            site_id = str(row["Site ID"]).strip()
            site = str(row["Site"]).strip()
            officer = str(row["Officer(s)"]).strip()

            if elapsed < 1200:
                errors.append(f"Row {idx+1}: Elapsed Time < 1200")
                continue
            if flow <= 0:
                errors.append(f"Row {idx+1}: Flow Rate must be > 0")
                continue
            if post < pre:
                errors.append(f"Row {idx+1}: Post Weight < Pre Weight")
                continue
            if not site_id or not site or not officer:
                errors.append(f"Row {idx+1}: Missing required fields (Site ID, Site, Officer)")
                continue

            valid_rows.append(row.tolist())
        except Exception as e:
            errors.append(f"Row {idx+1}: Error parsing values")

    if valid_rows:
        try:
            # Check or create sheet
            if CALC_SHEET in [ws.title for ws in spreadsheet.worksheets()]:
                sheet = spreadsheet.worksheet(CALC_SHEET)
            else:
                sheet = spreadsheet.add_worksheet(title=CALC_SHEET, rows="100", cols="20")
                sheet.append_row(edited_df.columns.tolist())

            for row in valid_rows:
                sheet.append_row(row)
            st.success(f"✅ {len(valid_rows)} records saved successfully.")
        except Exception as e:
            st.error(f"❌ Failed to save data: {e}")
    else:
        st.warning("⚠ No valid rows to save. See below for validation issues.")
    
    if errors:
        for err in errors:
            st.error(err)
