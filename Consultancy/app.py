
import streamlit as st
import streamlit.components.v1 as components
import gspread
from oauth2client.service_account import ServiceAccountCredentials

from admin.show import show
from admin.user_management import admin_panel

from components import (
    pm_form,
    noise,
    pm_calculation,
    apartment
)

from modules.authentication import login, logout_button
from modules.user_utils import ensure_users_sheet
from resource import load_data_from_sheet, sheet, spreadsheet
from constants import MERGED_SHEET, CALC_SHEET, USERS_SHEET, SPREADSHEET_ID














# ------------------------
# 1. Google Sheets Auth
# ------------------------
creds_dict = st.secrets["GOOGLE_CREDENTIALS"]
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)
spreadsheet = client.open_by_key(SPREADSHEET_ID)
users_sheet = ensure_users_sheet(spreadsheet)

# ------------------------
# 2. User Authentication
# ------------------------
logged_in, authenticator = login(users_sheet)
if not logged_in:
    st.stop()

# ------------------------














# ------------------------
# 4. User Info Display
# ------------------------
username = st.session_state.get("username")
role = st.session_state.get("role")




if "df" not in st.session_state:
    with st.spinner("🔄 Loading data..."):
        st.session_state.df = load_data_from_sheet(sheet)
        st.session_state.sheet = sheet
        st.session_state.spreadsheet = spreadsheet
# ------------------------
# 5. Role-Based Navigation
# ------------------------
role_pages = {
    "admin": [
        ("🏠 Home", "Home"),
        ("🦺 Particulate Matter", "Particulate Matter"),
        ("✍️ Noise/Stack/VOC/Gases", "Noise/Stack/VOC/Gases"),
        ("☘️ PM Calculation", "PM Calculation"),
        ("⚙️ Admin Panel", "Admin Panel")
    ],
    "officer": [
        ("🏠 Home", "Home"),
        ("🦺 Particulate Matter", "Particulate Matter"),
        ("✍️ Noise/Stack/VOC/Gases", "Noise/Stack/VOC/Gases"),
        ("☘️ PM Calculation", "PM Calculation")
    ],
    "supervisor": [
        ("🏠 Home", "Home"),
        ("⚙️ Admin Panel", "Admin Panel"),
    ]
}

pages_with_icons = role_pages.get(role, [])
pages = [p[1] for p in pages_with_icons]

if "selected_page" not in st.session_state or st.session_state["selected_page"] not in pages:
    st.session_state["selected_page"] = pages[0] if pages else None

# ------------------------
# 6. Styled Sidebar Navigation
# ------------------------

with st.sidebar:
    st.title("📁 Navigation")
    selected_page = st.radio(
        "Go to",
        options=[p[0] for p in pages_with_icons],
        index=pages.index(st.session_state["selected_page"]) if st.session_state["selected_page"] else 0,
        key="nav_radio"
    )
    for label, page in pages_with_icons:
        if label == selected_page:
            st.session_state["selected_page"] = page
            break
    st.markdown("---")
    logout_button(authenticator)
    

# ------------------------
# 7. Page Routing
# ------------------------
choice = st.session_state.get("selected_page")

if choice == "Home":
    apartment.show()
elif choice == "Particulate Matter":
    pm_form.show()
elif choice == "PM Calculation":
    pm_calculation.show()
elif choice == "Noise/Stack/VOC/Gases":
    noise.show()
elif choice == "Admin Panel":
    admin_panel()

st.markdown("""
<hr>
<div style="
    text-align: center;
    color: var(--color-text);
    font-size: 0.9em;
">
    © 2025 EPA Ghana · Developed by Clement Mensah Ackaah 🦺 · Built with 😍 using Streamlit |
    <a href="mailto:clement.ackaah@epa.gov.gh" style="color: var(--color-text); text-decoration: underline;">
        Contact Support
    </a>
</div>
""", unsafe_allow_html=True)
