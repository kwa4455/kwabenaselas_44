import streamlit as st
import pandas as pd
from datetime import datetime
from utils import (
    load_data_from_sheet,
    add_data,
    merge_start_stop,
    save_merged_data_to_sheet,
    display_and_merge_data,
    sheet,
    spreadsheet,
    require_roles
)
from constants import MERGED_SHEET,CALC_SHEET

require_roles("admin", "viewer")


# === Display Existing Data & Merge START/STOP ===
st.header("📊 Submitted Monitoring Records")
df = load_data_from_sheet(sheet)
display_and_merge_data(df, spreadsheet, MERGED_SHEET)


# --- View Saved Entries ---
st.subheader("📂 View Saved PM₂.₅ Entries")

try:
    calc_data = spreadsheet.worksheet(CALC_SHEET).get_all_records()
    df_calc = pd.DataFrame(calc_data)

    if not df_calc.empty:
        df_calc["Date"] = pd.to_datetime(df_calc["Date _Start"], errors="coerce").dt.date
        df_calc["PM₂.₅ (µg/m³)"] = pd.to_numeric(df_calc["PM₂.₅ (µg/m³)"], errors="coerce")

        with st.expander("🔍 Filter Saved Entries"):
            selected_date = st.date_input("📅 Filter by Date", value=None)
            selected_site = st.selectbox("📌 Filter by Site", options=["All"] + sorted(df_calc["Site"].unique()))

        filtered_df = df_calc.copy()
        if selected_date:
            filtered_df = filtered_df[filtered_df["Date _Start"] == selected_date]
        if selected_site != "All":
            filtered_df = filtered_df[filtered_df["Site"] == selected_site]

        st.dataframe(filtered_df, use_container_width=True)
    else:
        st.info("ℹ No saved entries yet.")
except Exception as e:
    st.error(f"❌ Failed to load saved entries: {e}")

with st.expander("🕵️ View Deleted Records"):
    try:
        deleted_sheet = spreadsheet.worksheet("Deleted Records")
        deleted_data = deleted_sheet.get_all_values()
        if len(deleted_data) > 1:
            df_deleted = pd.DataFrame(deleted_data[1:], columns=deleted_data[0])
            st.dataframe(df_deleted, use_container_width=True)
        else:
            st.info("No deleted records found.")
    except Exception as e:
        st.warning("Deleted Records sheet not found or not accessible.")


