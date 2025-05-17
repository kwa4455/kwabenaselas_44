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
    if not {"Elapsed Time Diff (min)", "Average Flow Rate (L/min)"}.issubset(df_merged.columns):
        st.error("❌ Required columns 'Elapsed Time Diff (min)' or 'Average Flow Rate (L/min)' not found.")
        st.stop()
except Exception as e:
    st.error(f"❌ Failed to load merged sheet: {e}")
    st.stop()

# --- Site Filter (Single Select) ---
if "Site" in df_merged.columns:
    try:
        # Sort by Date_Start descending to get the latest
        available_sites = sorted(df_merged["Site"].dropna().unique())
        site_options = ["All Sites"] + available_sites

        # Default to most recent site in data (first row after sorting)
        most_recent_site = df_merged["Site"].dropna().iloc[0] if not df_merged.empty else "All Sites"

        selected_site = st.selectbox(
            "📍 Select Site", options=site_options, index=site_options.index(most_recent_site)
        )

        if selected_site != "All Sites":
            filtered_df = df_merged[df_merged["Site"] == selected_site]
        else:
            filtered_df = df_merged.copy()
    except Exception as e:
        st.warning(f"⚠ Could not auto-select most recent site: {e}")
        filtered_df = df_merged.copy()
else:
    st.warning("⚠ 'Site' column not found — skipping site filter.")
    filtered_df = df_merged.copy()

# --- Add Pre/Post Weight Columns ---
filtered_df["Pre Weight (g)"] = 0.0
filtered_df["Post Weight (g)"] = 0.0

# --- Data Editor ---
st.subheader("📊 Enter Weights")
edited_df = st.data_editor(
    filtered_df,
    num_rows="dynamic",
    use_container_width=True,
    column_config={
        "Pre Weight (g)": st.column_config.NumberColumn("Pre Weight (g)", help="Mass before sampling (grams)"),
        "Post Weight (g)": st.column_config.NumberColumn("Post Weight (g)", help="Mass after sampling (grams)")
    },
    disabled=[col for col in filtered_df.columns if col not in ["Pre Weight (g)", "Post Weight (g)"]],
)

# --- PM₂.₅ Calculation ---
def calculate_pm(row):
    try:
        elapsed = float(row["Elapsed Time Diff (min)"])
        flow = float(row["Average Flow Rate (L/min)"])
        pre_g = float(row["Pre Weight (g)"])
        post_g = float(row["Post Weight (g)"])
        mass_mg = (post_g - pre_g) * 1000  # g → mg

        if elapsed < 1200:
            return "Elapsed < 1200"
        if flow <= 0.05:
            return "Invalid Flow"
        if post_g < pre_g:
            return "Post < Pre"

        volume_m3 = (flow * elapsed) / 1000  # L → m³
        conc = (mass_mg * 1000) / volume_m3  # mg → µg, µg/m³

        return round(conc, 2)
    except:
        return "Error"

# --- Apply Calculation ---
edited_df["PM₂.₅ (µg/m³)"] = edited_df.apply(calculate_pm, axis=1)

# --- Show Table ---
st.subheader("📊 Calculated Results")
st.dataframe(edited_df, use_container_width=True)

# --- Save Valid Entries ---
if st.button("✅ Save Valid Entries"):
    valid_rows = []
    errors = []

    for idx, row in edited_df.iterrows():
        try:
            elapsed = float(row["Elapsed Time Diff (min)"])
            flow = float(row["Average Flow Rate (L/min)"])
            pre = float(row["Pre Weight (g)"])
            post = float(row["Post Weight (g)"])
            pm = calculate_pm(row)

            if isinstance(pm, str):
                errors.append(f"Row {idx + 1}: {pm}")
                continue

            # Use Date_Start if available, otherwise today
            date_value = row.get("Date_Start", datetime.today().date())
            try:
                date_str = str(pd.to_datetime(date_value).date())
            except:
                date_str = str(datetime.today().date())

            site_id = str(row.get("ID", "")).strip()
            site = str(row.get("Site", "")).strip()
            officer = str(row.get("Monitoring Officer_Start", "")).strip()

            if not all([site_id, site, officer]):
                errors.append(f"Row {idx + 1}: Missing required fields (ID, Site, Officer)")
                continue

            valid_rows.append([
                date_str, site_id, site, officer, elapsed, flow, pre, post, pm
            ])
        except Exception as e:
            errors.append(f"Row {idx + 1}: Error parsing row - {e}")

    if valid_rows:
        try:
            # Ensure sheet exists
            sheet_titles = [ws.title for ws in spreadsheet.worksheets()]
            if CALC_SHEET not in sheet_titles:
                calc_ws = spreadsheet.add_worksheet(title=CALC_SHEET, rows="1000", cols="20")
                header = ["Date", "Site ID", "Site", "Officer(s)", "Elapsed Time (min)", "Flow Rate (L/min)",
                          "Pre Weight (g)", "Post Weight (g)", "PM₂.₅ (µg/m³)"]
                calc_ws.append_row(header)
            else:
                calc_ws = spreadsheet.worksheet(CALC_SHEET)

            for row in valid_rows:
                calc_ws.append_row(row)

            st.success(f"✅ Saved {len(valid_rows)} valid entries.")
        except Exception as e:
            st.error(f"❌ Failed to save data: {e}")
    else:
        st.warning("⚠ No valid rows to save.")

    if errors:
        st.error("Some rows were invalid:")
        for e in errors:
            st.text(f"- {e}")
