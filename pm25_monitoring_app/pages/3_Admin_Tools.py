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
require_roles("admin")  # Only admins can proceed

st.success(f"Welcome **{st.session_state['username']}**! You are an **{st.session_state['role']}**.")


# === Display Existing Data & Merge START/STOP ===
st.header("📊 Submitted Monitoring Records")
df = load_data_from_sheet(sheet)
display_and_merge_data(df, spreadsheet, MERGED_SHEET)
# Display Calculated Table
st.subheader("Calculated Results")
# --- Footer ---
st.markdown("""
    <hr style="margin-top: 40px; margin-bottom:10px">
    <div style='text-align: center; color: grey; font-size: 0.9em;'>
        © 2025 EPA Ghana · Developed by Clement Mensah Ackaah · Built with ❤️ using Streamlit
    </div>
""", unsafe_allow_html=True)
