import streamlit as st
import pandas as pd
from utils import (
    load_data_from_sheet,
    delete_row,
    delete_merged_record_by_index,
    sheet,
    spreadsheet,
    require_roles
)
from constants import MAIN_SHEET, MERGED_SHEET

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

# --- Delete from Merged Records ---
st.subheader("🗑️ Delete from Merged Records")
df_merged = load_data_from_sheet(sheet, MERGED_SHEET)

if df_merged.empty:
    st.info("No merged records available.")
else:
    df_merged["Index"] = df_merged.index
    df_merged["Merged Record"] = df_merged.apply(
        lambda x: f"{x['ID']} | {x['Site']} | {x['Start Date']} to {x['Stop Date']}", axis=1
    )

    selected_merged = st.selectbox("Select merged record to delete:", [""] + df_merged["Merged Record"].tolist())

    if selected_merged:
        index_to_delete = int(df_merged[df_merged["Merged Record"] == selected_merged]["Index"].values[0])
        
        if st.checkbox("✅ Confirm deletion of merged record"):
            if st.button("🗑️ Delete Merged Record"):
                delete_merged_record_by_index(index_to_delete)
                st.success("✅ Merged record deleted and backed up successfully.")
                st.experimental_rerun()



# --- Footer ---
st.markdown("""
    <hr style="margin-top: 40px; margin-bottom:10px">
    <div style='text-align: center; color: grey; font-size: 0.9em;'>
        © 2025 EPA Ghana · Developed by Clement Mensah Ackaah · Built with ❤️ using Streamlit
    </div>
""", unsafe_allow_html=True)
