import streamlit as st
import pandas as pd
from utils import (
    load_data_from_sheet,
    delete_row,
    delete_merged_record_by_index,
    display_and_merge_data,
    sheet,
    spreadsheet,
    require_roles
)
from constants import MAIN_SHEET,MERGED_SHEET, CALC_SHEET

# --- Page Setup ---
st.title("🔧 Admin Tools")
require_roles("admin","viewer")  # Only admins can proceed

st.success(f"Welcome **{st.session_state['username']}**! You are an **{st.session_state['role']}**.")


# === Display Existing Data & Merge START/STOP ===
st.header("📊 Submitted Monitoring Records")
df = load_data_from_sheet(sheet)
display_and_merge_data(df, spreadsheet, MERGED_SHEET)
# Display Calculated Table
# --- Show Saved Entries ---
st.subheader("📦 Saved PM₂.₅ Entries")

try:
    calc_ws = spreadsheet.worksheet(CALC_SHEET)
    records = calc_ws.get_all_records()
    if records:
        df_saved = pd.DataFrame(records)
        st.dataframe(df_saved, use_container_width=True)
    else:
        st.info("ℹ No entries have been saved yet.")
except Exception as e:
    st.error(f"❌ Failed to load saved data: {e}")

# --- Footer ---
st.markdown("""
    <hr style="margin-top: 40px; margin-bottom:10px">
    <div style='text-align: center; color: grey; font-size: 0.9em;'>
        © 2025 EPA Ghana · Developed by Clement Mensah Ackaah · Built with ❤️ using Streamlit
    </div>
""", unsafe_allow_html=True)
