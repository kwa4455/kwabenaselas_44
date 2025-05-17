import streamlit as st
from utils import login, load_data_from_sheet, sheet, spreadsheet, logout_button

# Page config and login
st.set_page_config(page_title="PM₂.₅ Monitoring App", layout="wide")
login()

# Access session info
username = st.session_state["username"]
role = st.session_state["role"]

# Load data once
if "df" not in st.session_state:
    with st.spinner("Loading data..."):
        st.session_state.df = load_data_from_sheet(sheet)
        st.session_state.sheet = sheet
        st.session_state.spreadsheet = spreadsheet

# --- Custom Header ---
st.markdown("""
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
        grid-template-columns: repeat(2, 1fr);
        gap: 2rem;
        margin-top: 2rem;
    }
    .card {
        border: 2px solid #d0d0d0;
        border-radius: 15px;
        padding: 2rem;
        text-align: center;
        box-shadow: 2px 2px 8px #ccc;
        transition: all 0.3s ease-in-out;
    }
    .card:hover {
        box-shadow: 4px 4px 12px #bbb;
        transform: scale(1.02);
    }
    .card-icon {
        font-size: 2rem;
    }
    .card-title {
        font-size: 1.2rem;
        font-weight: bold;
        margin-top: 1rem;
    }
    .card-desc {
        color: #444;
        font-size: 0.9rem;
        margin-top: 0.5rem;
    }
    .card a {
        display: inline-block;
        margin-top: 1rem;
        font-weight: bold;
        text-decoration: none;
        color: #2c7c70;
    }
</style>

<div class="header-bar">
    <div class="header-title">PM₂.₅ Monitoring</div>
    <div class="header-links">
        <a href="#">Login</a>
        <a href="#">Register</a>
        <a href="#">Forgot password?</a>
    </div>
</div>
""", unsafe_allow_html=True)

# --- Title and Info ---
st.title("🇬🇭 EPA Ghana | PM₂.₅ Monitoring App")
st.info(f"👤 Logged in as: **{username}** (Role: {role})")

# --- Sidebar Navigation ---
st.sidebar.title("📁 Navigation")
st.sidebar.page_link("main.py", label="Main", icon="🏠")
if role in ["admin", "collector"]:
    st.sidebar.page_link("pages/1_Data_Entry.py", label="Data Entry", icon="📝")
if role in ["admin", "editor", "collector"]:
    st.sidebar.page_link("pages/2_Edit_Record.py", label="Edit Records", icon="✏️")
st.sidebar.page_link("pages/3_PM25_Calculation.py", label="PM₂.₅ Calculation", icon="📊")
if role == "admin":
    st.sidebar.page_link("pages/4_Admin_Tools.py", label="Admin Tools", icon="🛠️")

# --- Main Card UI ---
st.markdown('<div class="grid-container">', unsafe_allow_html=True)

# Card Generator
def render_card(icon, title, desc, page_path):
    st.markdown(f"""
    <div class="card">
        <div class="card-icon">{icon}</div>
        <div class="card-title">{title}</div>
        <div class="card-desc">{desc}</div>
        <a href="{page_path}" target="_self">Go →</a>
    </div>
    """, unsafe_allow_html=True)

if role in ["admin", "collector"]:
    render_card("✅", "Data Entry", "Add new data entry", "pages/1_Data_Entry.py")

if role in ["admin", "editor", "collector"]:
    render_card("✏️", "Edit Records", "Modify or delete records", "pages/2_Edit_Records.py")

render_card("📊", "PM₂.₅ Calculation", "Calculate PM₂.₅ concentrations", "pages/3_PM25_Calculation.py")

if role == "admin":
    render_card("🛠️", "Admin Tools", "Access admin utilities", "pages/4_Admin_Tools.py")

st.markdown("</div>", unsafe_allow_html=True)

# --- Logout Button ---
logout_button()
