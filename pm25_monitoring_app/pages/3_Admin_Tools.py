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
from constants import MAIN_SHEET,MERGED_SHEET

# --- Page Setup ---
st.title("🔧 Admin Tools")
require_roles("admin")  # Only admins can proceed

st.success(f"Welcome **{st.session_state['username']}**! You are an **{st.session_state['role']}**.")

# --- Delete from Submitted Records ---
st.subheader("🗑️ Delete from Submitted Records")
df_submitted = load_data_from_sheet(sheet)

if df_submitted.empty:
    st.info("No submitted records available.")
else:
    df_submitted["Row Number"] = df_submitted.index + 2  # Google Sheets is 1-indexed + header
    df_submitted["Record ID"] = df_submitted.apply(
        lambda x: f"{x['Entry Type']} | {x['ID']} | {x['Site']} | {x['Submitted At']}", axis=1
    )

    selected_record = st.selectbox("Select submitted record to delete:", [""] + df_submitted["Record ID"].tolist())

    if selected_record:
        row_to_delete = int(df_submitted[df_submitted["Record ID"] == selected_record]["Row Number"].values[0])
        
        if st.checkbox("✅ Confirm deletion of submitted record"):
            if st.button("🗑️ Delete Submitted Record"):
                delete_row(sheet, row_to_delete)
                st.success("✅ Submitted record deleted and backed up successfully.")
                st.experimental_rerun()


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
