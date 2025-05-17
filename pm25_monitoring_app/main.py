import streamlit as st
from utils import login, load_data_from_sheet, sheet, spreadsheet, logout_button

st.set_page_config(page_title="PM₂.₅ Monitoring App", layout="wide")
login()

username = st.session_state["username"]
role = st.session_state["role"]

# Load data if not already loaded
if "df" not in st.session_state:
    with st.spinner("Loading data..."):
        st.session_state.df = load_data_from_sheet(sheet)
        st.session_state.sheet = sheet
        st.session_state.spreadsheet = spreadsheet

# --- HEADER & CSS ---
st.markdown("""
<link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css" rel="stylesheet">

<style>
    .header-bar {
        background-color: #2c7c70;
        padding: 1rem 2rem;
        color: white;
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 1.2rem;
        border-radius: 0 0 8px 8px;
    }
    .header-title {
        font-weight: bold;
    }
    .header-links a {
        color: white;
        margin-left: 20px;
        text-decoration: none;
    }
    .grid-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 1.5rem;
        margin-top: 2rem;
    }
    .card {
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        box-shadow: 2px 2px 8px #aaa;
        transition: transform 0.2s;
    }
    .card:hover {
        transform: scale(1.02);
    }
    .card-icon {
        font-size: 2.5rem;
    }
    .card-title {
        font-size: 1.2rem;
        font-weight: bold;
        margin-top: 1rem;
    }
    .card-desc {
        font-size: 0.9rem;
        margin-top: 0.5rem;
    }
</style>

<div class="header-bar">
    <div class="header-title">PM₂.₅ Monitoring Dashboard</div>
    <div class="header-links">
        <a href="#">Login</a>
        <a href="#">Register</a>
        <a href="#">Forgot Password?</a>
    </div>
</div>
""", unsafe_allow_html=True)

# --- TITLE ---
st.title("🇬🇭 EPA Ghana | PM₂.₅ Monitoring App")
st.info(f"👤 Logged in as: **{username}** (Role: {role})")

# --- SIDEBAR ---
st.sidebar.title("📁 Navigation")
st.sidebar.page_link("main.py", label="Home", icon="🏠")
if role in ["admin", "collector"]:
    st.sidebar.page_link("pages/1_Data_Entry.py", label="Data Entry", icon="📝")
if role in ["admin", "editor", "collector"]:
    st.sidebar.page_link("pages/2_Edit_Records.py", label="Edit Records", icon="✏️")
st.sidebar.page_link("pages/3_PM25_Calculation.py", label="PM₂.₅ Calculation", icon="📊")
if role == "admin":
    st.sidebar.page_link("pages/4_Admin_Tools.py", label="Admin Tools", icon="🛠️")

# --- CARD RENDERING (uses st.page_link) ---
st.markdown('<div class="grid-container">', unsafe_allow_html=True)

def card(icon_class, title, desc, page_path, bg_color):
    with st.container():
        st.markdown(f"""
        <div class="card" style="background-color: {bg_color};">
            <div class="card-icon"><i class="{icon_class}"></i></div>
            <div class="card-title">{title}</div>
            <div class="card-desc">{desc}</div>
        </div>
        """, unsafe_allow_html=True)
        st.page_link(page_path, label="Go →")

# Render cards by role
if role in ["admin", "collector"]:
    card("fas fa-plus-circle", "Data Entry", "Add new data entries", "pages/1_Data_Entry.py", "#4CAF50")
if role in ["admin", "editor", "collector"]:
    card("fas fa-edit", "Edit Records", "Modify or delete records", "pages/2_Edit_Records.py", "#2196F3")

card("fas fa-chart-line", "PM₂.₅ Calculation", "Compute concentration values", "pages/3_PM25_Calculation.py", "#FF9800")

if role == "admin":
    card("fas fa-cogs", "Admin Tools", "System utilities and admin controls", "pages/4_Admin_Tools.py", "#9C27B0")

st.markdown('</div>', unsafe_allow_html=True)

# --- Logout ---
logout_button()
