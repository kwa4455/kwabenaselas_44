import streamlit as st
from streamlit_option_menu import option_menu
from auth.login import login_user
from auth.logout import logout_user
from pages import data_entry, review_records, edit_records
from admin import show as admin_panel  # 👈 import the admin panel
from supabase_client import supabase
from utils import load_data_from_sheet, sheet, spreadsheet

# App configuration
st.set_page_config(page_title="EPA Ghana | Air Quality Field Data Entry", layout="centered", page_icon="🌍")

# Inject styles (make sure this is defined somewhere)
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
        pages = ["📥 Data Entry", "✏️ Edit Records", "🗂️ Review", "⚙️ Admin Panel"]
    elif role == "collector":
        pages = ["📥 Data Entry", "✏️ Edit Records"]
    elif role == "editor":
        pages = ["✏️ Edit Records", "🗂️ Review"]
    elif role == "viewer":
        pages = ["🗂️ Review"]

    choice = option_menu(
        menu_title="Go to",
        options=pages,
        icons=["cloud-upload", "pencil", "folder", "gear"][:len(pages)],
        menu_icon="cast",
        default_index=0,
    )

    st.markdown("---")
    logout_user()

# Route page
if choice == "📥 Data Entry":
    data_entry.show()
elif choice == "✏️ Edit Records":
    edit_records.show()
elif choice == "🗂️ Review":
    review_records.show()
elif choice == "⚙️ Admin Panel":
    admin_panel()
