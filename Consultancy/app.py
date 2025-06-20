
import streamlit as st
import streamlit.components.v1 as components
import gspread
from oauth2client.service_account import ServiceAccountCredentials

from admin.show import show
from admin.user_management import admin_panel

from components import (
    pm_form,
    env_form,
    pm_calculation,
    apartment
)

from modules.authentication import login, logout_button
from modules.user_utils import ensure_users_sheet
from resource import load_data_from_sheet, sheet, spreadsheet
from constants import MERGED_SHEET, CALC_SHEET, USERS_SHEET, SPREADSHEET_ID



st.markdown("""
<style>
/* GLOBAL */
* {
    transition: all 0.2s ease-in-out;
    font-family: 'Segoe UI', sans-serif;
}

/* App background */
html, .stApp {
    background: url('https://i.postimg.cc/pTr1rWy0/blur-chemistry-equipments-laboratory-background-260nw-391560133.webp');
    background-size: cover;
    background-position: center;
    min-height: 100vh;
    backdrop-filter: blur(40px);
}

/* Main content container glass style */
.logged_in {
    background: rgba(255, 255, 255, 0.2);
    border-radius: 16px;
    padding: 20px;
    margin: 20px auto;
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    border: 1px solid rgba(255, 255, 255, 0.3);
    width: 80%;
}

/* Text Input Fields */
div[data-testid="stTextInput"] input {
    background: rgba(255, 255, 255, 0.25) !important;
    border: 1px solid rgba(255, 255, 255, 0.4) !important;
    border-radius: 10px !important;
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
    color: #000 !important;
}

/* Text Area Fields */
div[data-testid="stTextArea"] textarea {
    background: rgba(255, 255, 255, 0.25) !important;
    border: 1px solid rgba(255, 255, 255, 0.4) !important;
    border-radius: 10px !important;
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
    color: #000 !important;
}
/* Info alert (Logged in as...) */
div[data-testid="stAlert-info"] {
    background: rgba(255, 255, 255, 0.25) !important;
    color: #000 !important;
    border-radius: 12px !important;
    border: 1px solid rgba(255, 255, 255, 0.3) !important;
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
    padding: 16px !important;
    font-weight: 500;
}

/* Optional: info icon color */
div[data-testid="stAlert-info"] svg {
    color: #0099cc !important;
}
/* Buttons */
button[data-testid="baseButton-primary"] {
    background: rgba(255, 255, 255, 0.25) !important;
    color: #000 !important;
    border: 1px solid rgba(255, 255, 255, 0.3) !important;
    border-radius: 12px !important;
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
}

button[data-testid="baseButton-primary"]:hover {
    background: rgba(255, 255, 255, 0.35) !important;
    box-shadow: 0 6px 14px rgba(0, 0, 0, 0.25);
}
div[data-testid="stForm"] {
    background: rgba(255, 255, 255, 0.18);
    border-radius: 16px;
    padding: 24px;
    margin-top: 10px;
    margin-bottom: 30px;
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.2);
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
    border: 1px solid rgba(255, 255, 255, 0.25);
}
/* Selectbox */
div[data-testid="stSelectbox"] {
    background: rgba(255, 255, 255, 0.25) !important;
    border-radius: 12px;
    padding: 6px 12px;
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
    border: 1px solid rgba(255, 255, 255, 0.3);
    color: #000 !important;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}
/* Optional - make sidebar translucent */
section[data-testid="stSidebar"] {
    background: rgba(255, 255, 255, 0.15);
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    border-right: 1px solid rgba(255, 255, 255, 0.2);
    box-shadow: 2px 0 10px rgba(0, 0, 0, 0.1);
}
/* Slider */
div[data-testid="stSlider"] {
    background: rgba(255, 255, 255, 0.2);
    border-radius: 12px;
    padding: 10px;
    backdrop-filter: blur(6px);
    -webkit-backdrop-filter: blur(6px);
    box-shadow: 0 3px 8px rgba(0, 0, 0, 0.2);
}

/* Slider handle and track text */
div[data-testid="stSlider"] .stSlider > div {
    color: #000 !important;
}

/* Dataframe / Table Styling */
.css-1d391kg, .css-1r6slb0, .stDataFrame, .stTable {
    background: rgba(255, 255, 255, 0.2) !important;
    border-radius: 10px !important;
    backdrop-filter: blur(10px) !important;
    -webkit-backdrop-filter: blur(10px) !important;
    color: black !important;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
}
hr {
    border: none;
    border-top: 1px solid rgba(255, 255, 255, 0.3);
}

.footer-text {
    color: rgba(255, 255, 255, 0.7);
}
/* Table Cells */
thead, tbody, tr, th, td {
    background: rgba(255, 255, 255, 0.15) !important;
    color: #000 !important;
    backdrop-filter: blur(4px);
}

/* Sidebar Styling */
section[data-testid="stSidebar"] {
    background: rgba(255, 255, 255, 0.15);
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    border-right: 1px solid rgba(255, 255, 255, 0.2);
    box-shadow: 2px 0 10px rgba(0, 0, 0, 0.1);
}
</style>
""", unsafe_allow_html=True)











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

st.markdown("""
<style>
/* General alert box (st.info, st.warning, etc.) */
div[role="alert"] {
    background: rgba(255, 255, 255, 0.25) !important;
    color: #000 !important;
    border-radius: 12px !important;
    border: 1px solid rgba(255, 255, 255, 0.3) !important;
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
    padding: 16px !important;
    font-weight: 500;
}

/* Optional: override icon color for st.info */
div[role="alert"] svg {
    color: #0066cc !important; /* blue tone for info */
}
</style>
""", unsafe_allow_html=True)

st.info(f"👤 Logged in as: **{username}** (Role: {role})")



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
        ("✍️ Other Measurement", "Other Measurement"),
        ("☘️ PM Calculation", "PM Calculation"),
        ("⚙️ Admin Panel", "Admin Panel")
    ],
    "officer": [
        ("🏠 Home", "Home"),
        ("🦺 Particulate Matter", "Particulate Matter"),
        ("✍️ Other Measurement", "Other Measurement"),
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
st.markdown("""
    <style>
    div[role="radiogroup"] > label > div > input[type="radio"] {
        display: none;
    }
    div[role="radiogroup"] > label {
        display: block;
        cursor: pointer;
        user-select: none;
        padding: 12px 15px;
        margin: 5px 0;
        font-size: 16px;
        color: #444;
        background-color: rgba(255, 255, 255, 0.15);
        border-radius: 8px;
        transition: background-color 0.3s ease, color 0.3s ease;
        font-weight: 600;
        font-family: 'Inter', sans-serif;
    }
    div[role="radiogroup"] > label:hover {
        background-color: rgba(255, 255, 255, 0.3);
        color: #20B2AA;
    }
    div[role="radiogroup"] > label[data-baseweb="option"]:has(input[type="radio"]:checked) {
        background-color: #20B2AA;
        color: white;
        box-shadow: 0 0 8px #20B2AA;
    }
    </style>
""", unsafe_allow_html=True)

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
elif choice == "Other Measurement":
    env_form.show()
elif choice == "PM Calculation":
    pm_calculation.show()
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
