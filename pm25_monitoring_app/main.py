import streamlit as st
import sys
import os


from streamlit_option_menu import option_menu
from auth.login import login_user
from auth.logout import logout_user
from components import (
    data_entry_form,
    edit_data_entry_form,
    pm25_calculation,
    supervisor_review_section
)
from .show import show
from .user_management import admin_panel, require_admin
from supabase_client import supabase
from utils import load_data_from_sheet, sheet, spreadsheet

# App configuration
st.set_page_config(page_title="EPA Ghana | Air Quality Field Data Entry", layout="centered", page_icon="🌍")

# Inject styles (define CSS globally)
def inject_global_css():
    st.markdown(
        """
        <style>
        .css-18e3th9 {padding-top: 1rem;}
        </style>
        """,
        unsafe_allow_html=True,
    )

inject_global_css()

# Login check
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# Show login form if not logged in
if not st.session_state.logged_in:
    login_user()
    st.stop()

# Role and user info
username = st.session_state.get("username")
role = st.session_state.get("role")

# App header
st.title("🇬🇭 EPA Ghana | PM2.5 Field Data Platform")
st.info(f"👤 Logged in as: **{username}** (Role: `{role}`)")

# Load data once into session state
if "df" not in st.session_state:
    with st.spinner("🔄 Loading data..."):
        st.session_state.df = load_data_from_sheet(sheet)
        st.session_state.sheet = sheet
        st.session_state.spreadsheet = spreadsheet

# Sidebar navigation
with st.sidebar:
    st.title("📁 Navigation")

    pages = []
    if role == "admin":
        pages = ["📥 Data Entry Form", "✏️ Edit Data Entry Form", "🗂️ PM25 Calculation", "⚙️ Admin Panel"]
    elif role == "collector":
        pages = ["📥 Data Entry Form", "✏️ Edit Data Entry Form"]
    elif role == "editor":
        pages = ["✏️ Edit Data Entry Form", "🗂️ PM25 Calculation"]
    elif role == "viewer":
        pages = ["🗂️ PM25 Calculation"]

    choice = option_menu(
        menu_title="Go to",
        options=pages,
        icons=["cloud-upload", "pencil", "folder", "gear"][:len(pages)],
        menu_icon="cast",
        default_index=0,
    )

    st.markdown("---")
    logout_user()

if choice == "📥 Data Entry Form":
    data_entry_form.show()
elif choice == "✏️ Edit Data Entry Form":
    edit_data_entry_form.show()
elif choice == "🗂️ PM25 Calculation":
    pm25_calculation.show()
elif choice == "🗂️ Supervisor Review Section":
    supervisor_review_section.show()
elif choice == "⚙️ Admin Panel":
    admin_panel()
