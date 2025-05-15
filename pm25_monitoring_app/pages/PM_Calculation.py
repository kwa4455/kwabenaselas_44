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
except Exception as e:
    st.error("Failed to load merged records data.")
    site_ids = []
    site_names = []

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

# Display Calculated Data
st.subheader("Calculated Results")
st.dataframe(edited_df, use_container_width=True)

# Save Valid Rows to Google Sheets
if st.button("✅ Save Valid Entries"):
    valid_rows = edited_df[edited_df["PM₂.₅ (µg/m³)"].apply(lambda x: isinstance(x, float))]
    if not valid_rows.empty:
        try:
            # Check or create sheet
            if CALC_SHEET in [ws.title for ws in spreadsheet.worksheets()]:
                sheet = spreadsheet.worksheet(CALC_SHEET)
            else:
                sheet = spreadsheet.add_worksheet(title=CALC_SHEET, rows="100", cols="20")
                sheet.append_row(valid_rows.columns.tolist())

            # Save to Google Sheets
            for _, row in valid_rows.iterrows():
                sheet.append_row(row.tolist())
            st.success(f"✅ {len(valid_rows)} records saved successfully.")
        except Exception as e:
            st.error(f"❌ Failed to save data: {e}")
    else:
        st.warning("⚠ No valid rows to save. Ensure elapsed time is ≥ 1200 and values are correct.")
