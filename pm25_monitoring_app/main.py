import streamlit as st
from utils import login, load_data_from_sheet, sheet, spreadsheet, logout_button
from streamlit_js_eval import streamlit_js_eval


# Set page config
st.set_page_config(
    page_title="PM₂.₅ Monitoring App",
    layout="wide",
    page_icon="🌍"
)

# Get screen width on load
width_data = streamlit_js_eval(js_expressions="screen.width", key="SCR_WIDTH")

# Set flag
if width_data:
    st.session_state["is_mobile"] = width_data <= 768
else:
    st.session_state["is_mobile"] = False
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

# Handle authentication
login()

# Access session state
username = st.session_state["username"]
role = st.session_state["role"]

# App Header
st.title("🇬🇭 EPA Ghana | PM₂.₅ Monitoring App")
st.info(f"👤 Logged in as: **{username}** (Role: {role})")

# Load data once into session state
if "df" not in st.session_state:
    with st.spinner("🔄 Loading data..."):
        st.session_state.df = load_data_from_sheet(sheet)
        st.session_state.sheet = sheet
        st.session_state.spreadsheet = spreadsheet

# Define pages by role
if role == "admin":
    pages = ["📥 Data Entry", "✏️ Edit Records", "🗂️ Review"]
elif role == "editor":
    pages = ["✏️ Edit Records", "🗂️ Review"]
elif role == "viewer":
    pages = ["🔍 Review & Merge"]
elif role == "collector":
    pages = ["📥 Data Entry", "✏️ Edit Records"]
else:
    st.error("❌ Invalid role.")
    st.stop()


# Sidebar Navigation
st.sidebar.title("📁 Navigation")
selected_page = st.sidebar.radio("Go to", pages)

# Show Logout
logout_button()

# Guide user
st.success(f"✅ Use the sidebar to access: **{selected_page}**")
