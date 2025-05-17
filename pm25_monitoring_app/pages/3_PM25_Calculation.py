import streamlit as st
import pandas as pd
from datetime import datetime
from utils import require_roles, spreadsheet
from constants import MERGED_SHEET, CALC_SHEET

# --- Page Setup ---
st.set_page_config(page_title="PM₂.₅ Calculator", page_icon="🧶")
st.title("🧶 PM₂.₅ Concentration Calculator")
st.write("Enter Pre and Post Weights to calculate PM₂.₅ concentrations in µg/m³.")

# --- Role Check ---
require_roles("admin", "editor")

# --- Load Merged Data ---
try:
    merged_data = spreadsheet.worksheet(MERGED_SHEET).get_all_records()
    df_merged = pd.DataFrame(merged_data)
    df_merged.columns = df_merged.columns.str.strip()

    if not {"Elapsed Time Diff (min)", "Average Flow Rate (L/min)"}.issubset(df_merged.columns):
        st.error("❌ Required columns missing: 'Elapsed Time Diff (min)', 'Average Flow Rate (L/min)'")
        st.stop()
except Exception as e:
    st.error(f"❌ Failed to load merged sheet: {e}")
    st.stop()

# --- Site Filter ---
if "Site" in df_merged.columns:
    try:
        available_sites = sorted(df_merged["Site"].dropna().unique())
        site_options = ["All Sites"] + available_sites
        most_recent_site = df_merged["Site"].dropna().iloc[0] if not df_merged.empty else "All Sites"

        selected_site = st.selectbox("📍 Select Site", options=site_options, index=site_options.index(most_recent_site))
        filtered_df = df_merged[df_merged["Site"] == selected_site] if selected_site != "All Sites" else df_merged.copy()
    except Exception as e:
        st.warning(f"⚠ Could not auto-select site: {e}")
        filtered_df = df_merged.copy()
else:
    st.warning("⚠ 'Site' column not found — skipping site filter.")
    filtered_df = df_merged.copy()

# --- Add Pre/Post Weight Columns ---
filtered_df["Pre Weight (g)"] = 0.0
filtered_df["Post Weight (g)"] = 0.0

# --- Data Editor ---
st.subheader("📊 Enter Weights")
editable_columns = ["Pre Weight (g)", "Post Weight (g)"]
edited_df = st.data_editor(
    filtered_df,
    num_rows="dynamic",
    use_container_width=True,
    column_config={
        "Pre Weight (g)": st.column_config.NumberColumn("Pre Weight (g)", help="Mass before sampling (grams)"),
        "Post Weight (g)": st.column_config.NumberColumn("Post Weight (g)", help="Mass after sampling (grams)")
    },
    disabled=[col for col in filtered_df.columns if col not in editable_columns],
)

# --- PM₂.₅ Calculation Function ---
def calculate_pm(row):
    try:
        elapsed = float(row["Elapsed Time Diff (min)"])
        flow = float(row["Average Flow Rate (L/min)"])
        pre = float(row["Pre Weight (g)"])
        post = float(row["Post Weight (g)"])
        mass_mg = (post - pre) * 1000  # g → mg

        if elapsed < 1200:
            return "Elapsed < 1200"
        if flow <= 0.05:
            return "Invalid Flow"
        if post < pre:
            return "Post < Pre"

        volume_m3 = (flow * elapsed) / 1000  # L → m³
        if volume_m3 == 0:
            return "Zero Volume"

        conc = (mass_mg * 1000) / volume_m3  # µg/m³
        return round(conc, 2)
    except Exception as e:
        return f"Error: {e}"

# --- Calculate PM₂.₅ ---
edited_df["PM₂.₅ (µg/m³)"] = edited_df.apply(calculate_pm, axis=1)

# --- Display Calculated Data ---
st.subheader("📊 Calculated Results")
st.dataframe(edited_df, use_container_width=True)

# --- CSV Export ---
csv = edited_df.to_csv(index=False).encode("utf-8")
st.download_button(
    label="⬇️ Download Results as CSV",
    data=csv,
    file_name="pm25_results.csv",
    mime="text/csv"
)



# --- Save Valid Entries ---
# --- Save Valid Entries ---
if st.button("✅ Save Valid Entries"):
    valid_rows = []
    errors = []

    for idx, row in edited_df.iterrows():
        try:
            pm = row["PM₂.₅ (µg/m³)"]

            if isinstance(pm, str):
                errors.append(f"Row {idx + 1}: {pm}")
                continue

            # Ensure required fields are not empty (e.g., ID, Site, Officer)
            required_fields = ["ID", "Site", "Monitoring Officer_Start"]
            if not all(str(row.get(col, "")).strip() for col in required_fields):
                errors.append(f"Row {idx + 1}: Missing required fields (ID, Site, Officer)")
                continue

            # Prepare the row, ensuring all missing fields are replaced with empty strings
            data_row = []

            for col in final_header:
                value = row.get(col, "").strip() if pd.notna(row.get(col, "")) else ""
                
                # If it's a Date or Time column and is empty, you can use a placeholder or None
                if 'Date' in col or 'Time' in col:
                    value = value if value else None  # Set to None if empty, or you can set a default date
                data_row.append(value)

            # Log data_row to debug row content and size before saving
            st.write(f"Row {idx + 1} content: {data_row}")
            st.write(f"Row {idx + 1} length: {len(data_row)} | Header length: {len(final_header)}")

            # Check if the row matches the final_header length
            if len(data_row) != len(final_header):
                errors.append(f"Row {idx + 1}: Column mismatch ({len(data_row)} vs {len(final_header)})")
                continue

            valid_rows.append(data_row)

        except Exception as e:
            errors.append(f"Row {idx + 1}: Error parsing row - {e}")

    if valid_rows:
        try:
            sheet_titles = [ws.title for ws in spreadsheet.worksheets()]
            if CALC_SHEET not in sheet_titles:
                calc_ws = spreadsheet.add_worksheet(title=CALC_SHEET, rows="1000", cols=str(len(final_header)))
                calc_ws.append_row(final_header)
            else:
                calc_ws = spreadsheet.worksheet(CALC_SHEET)

            # Append rows in batch to Google Sheets
            calc_ws.append_rows(valid_rows, value_input_option="USER_ENTERED")

            st.success(f"✅ Saved {len(valid_rows)} valid entries.")
        except Exception as e:
            st.error(f"❌ Google Sheet save error: {e}")
    else:
        st.warning("⚠ No valid rows to save.")

    if errors:
        st.error("Some rows were invalid:")
        for err in errors:
            st.text(f"- {err}")

# --- Show Saved Entries ---
if st.checkbox("📖 Show Saved Entries in Sheet"):
    try:
        saved_data = spreadsheet.worksheet(CALC_SHEET).get_all_records(head=1)
        df_saved = pd.DataFrame(saved_data)
        st.dataframe(df_saved, use_container_width=True)
    except Exception as e:
        st.warning(f"⚠ Could not load saved entries: {e}")
