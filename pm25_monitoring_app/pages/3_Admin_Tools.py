# pages/3_Admin_Tools.py
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


# Admin Access Check
st.title("🔧 Admin Tools")


require_roles("admin")  # Only admins can proceed

st.success(f"Welcome **{st.session_state['user_email']}**! You are an **{st.session_state['role']}**.")

# === Delete from Submitted Records ===
st.subheader("Delete Submitted Record")
df_submitted = load_data_from_sheet(sheet)

if df_submitted.empty:
    st.info("No submitted records available.")
else:
    df_submitted["Row Number"] = df_submitted.index + 2
    df_submitted["Record ID"] = df_submitted.apply(
        lambda x: f"{x['Entry Type']} | {x['ID']} | {x['Site']} | {x['Submitted At']}", axis=1
    )

    selected_record = st.selectbox("Select record to delete:", [""] + df_submitted["Record ID"].tolist())

    if selected_record:
        row_to_delete = df_submitted[df_submitted["Record ID"] == selected_record]["Row Number"].values[0]
        
        # Deletion Confirmation Step
        if st.button("🗑️ Delete Submitted Record"):
            confirm = st.checkbox("Are you sure you want to delete this record?")
            if confirm:
                delete_row(sheet, row_to_delete)
                st.success("Submitted record deleted successfully.")
            else:
                st.warning("Please confirm the deletion.")

# === Delete from Merged Records ===
st.subheader("Delete Merged Record")
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
        index_to_delete = df_merged[df_merged["Merged Record"] == selected_merged]["Index"].values[0]
        
        # Deletion Confirmation Step
        if st.button("🗑️ Delete Merged Record"):
            confirm = st.checkbox("Are you sure you want to delete this merged record?")
            if confirm:
                delete_merged_record_by_index(index_to_delete)
                st.success("Merged record deleted successfully.")
            else:
                st.warning("Please confirm the deletion.")
   
if st.button("Undo Last Deletion"):
    undo_last_delete(sheet)
st.success("Last deleted record has been restored!")







