import streamlit as st
import pandas as pd
from datetime import datetime
from utils import (
    load_data_from_sheet,
    add_data,
    merge_start_stop,
    save_merged_data_to_sheet,
    filter_dataframe,
    display_and_merge_data,
    sheet,
    spreadsheet,
    require_roles
)
from constants import MERGED_SHEET

require_roles("admin", "editor", "collector")


# === Display Existing Data & Merge START/STOP ===
st.header("📊 Submitted Monitoring Records")
df = load_data_from_sheet(sheet)
display_and_merge_data(df, spreadsheet, MERGED_SHEET)

# === Filter and Display Merged Records ===
st.header("🔎 Filtered Merged Records")
merged_sheet = spreadsheet.worksheet(MERGED_SHEET)
merged_df = pd.DataFrame(merged_sheet.get_all_records())

if not merged_df.empty:
    st.subheader("Filter Merged Records")
    filtered_merged_df = filter_dataframe(merged_df)
    st.dataframe(filtered_merged_df, use_container_width=True)
else:
    st.info("No merged records available yet.")
