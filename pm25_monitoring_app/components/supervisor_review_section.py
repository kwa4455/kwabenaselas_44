import streamlit as st
import pandas as pd
from datetime import datetime
from utils import (
    load_data_from_sheet,
    add_data,
    merge_start_stop,
    save_merged_data_to_sheet,
    delete_row,
    restore_specific_deleted_record,
    filter_by_site_and_date,
    make_unique_headers,
    display_and_merge_data,
    sheet,
    spreadsheet
)
from constants import MERGED_SHEET,CALC_SHEET

def show():
    st.subheader("📥 Supervisor Review Section")





st.set_page_config(page_title="Supervisor Review Section", page_icon="🕵️")

# Inject Google Fonts and custom CSS for glassmorphism and font clarity
st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap" rel="stylesheet">

    <style>
    /* === Global Font and Text Effects === */
    html, body, [class*="css"]  {
        font-family: 'Poppins', sans-serif;
        text-shadow: 0 1px 2px rgba(0,0,0,0.08);
        color: #1f1f1f;
        background-color: #f4f7fa;
    }

    /* === App Title Styling === */
    .main > div:first-child h1 {
        color: #0a3d62;
        font-size: 2.8rem;
        text-shadow: 0 2px 4px rgba(0,0,0,0.15);
        margin-bottom: 0.5rem;
    }

    /* === Sidebar Glass Effect === */
    section[data-testid="stSidebar"] {
        background: rgba(255, 255, 255, 0.12);
        backdrop-filter: blur(14px) saturate(160%);
        -webkit-backdrop-filter: blur(14px) saturate(160%);
        border: 1px solid rgba(255, 255, 255, 0.25);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.25);
    }

    /* === Sidebar Navigation Styling === */
    section[data-testid="stSidebar"] .st-radio > div {
        background: rgba(255, 255, 255, 0.85);
        color: #000;
        border-radius: 12px;
        padding: 0.4rem 0.6rem;
        margin-bottom: 0.5rem;
        transition: all 0.2s ease;
    }
    section[data-testid="stSidebar"] .st-radio > div:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
    }

    /* === Info box styling === */
    .stAlert {
        background-color: rgba(232, 244, 253, 0.9);
        border-left: 6px solid #1f77b4;
        border-radius: 8px;
        padding: 1rem;
    }

    /* === Success message styling === */
    .stSuccess {
        background-color: rgba(230, 255, 230, 0.9);
        border-left: 6px solid #33cc33;
        border-radius: 8px;
        padding: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# Centered title and subtitle
st.markdown(
    """
    <div style='text-align: center;'>
        <h2>👷🏽‍♀️ Supervisor Review Section </h2>
        <p style='color: grey;'>For Supervisors to review, inspect, and audit monitoring records</p>
    </div>
    <hr>
    """,
    unsafe_allow_html=True
)

st.write("This page will display records and allow Supervisors to inspect and audit records.")



# === Display Existing Data & Merge START/STOP ===
st.header("📡 Submitted Monitoring Records")
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

with st.expander("👷🏾‍♂️ View Deleted Records"):
    try:
        deleted_sheet = spreadsheet.worksheet("Deleted Records")
        deleted_data = deleted_sheet.get_all_values()

        if len(deleted_data) > 1:
            headers = make_unique_headers(deleted_data[0])
            rows = deleted_data[1:]

            import pandas as pd
            df_deleted = pd.DataFrame(rows, columns=headers)

            st.dataframe(df_deleted, use_container_width=True)
        else:
            st.info("No deleted records found.")
    except Exception as e:
        st.error(f"❌ Could not load Deleted Records: {e}")



# --- Footer ---
st.markdown("""
    <hr style="margin-top: 40px; margin-bottom:10px">
    <div style='text-align: center; color: grey; font-size: 0.9em;'>
        © 2025 EPA Ghana · Developed by Clement Mensah Ackaah 🦺 · Built with 🪾 using Streamlit
    </div>
""", unsafe_allow_html=True)
