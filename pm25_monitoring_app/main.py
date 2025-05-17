import streamlit as st
from utils import login, load_data_from_sheet, sheet, spreadsheet, logout_button

# Set page configuration
st.set_page_config(
    page_title="PM₂.₅ Monitoring App",
    layout="wide",
    page_icon="🌍"
)

# Inject custom CSS styling
st.markdown("""
    <style>
    /* Fonts and layout */
    html, body, [class*="css"]  {
        font-family: 'Segoe UI', sans-serif;
        background-color: #f6f9fc;
    }

    /* App title */
    .main > div:first-child h1 {
        color: #1f77b4;
        font-size: 2.8rem;
    }

    /* Info banner */
    .stAlert {
        background-color: #e8f4fd;
        border-left: 6px solid #1f77b4;
        padding: 1rem;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(to bottom, #006400, #228B22);
        color: white;
    }
    section[data-testid="stSidebar"] .st-radio > div {
        background-color: white;
        color: black;
        border-radius: 10px;
        padding: 0.3rem;
    }

    /* Success message */
    .stSuccess {
        background-color: #e6ffe6;
        border-left: 6px solid #33cc33;
    }
    </style>
""", unsafe_allow_html=True)

# Login or stop if not authenticated
login()

# Access session state
username = st.session_state["username"]
role = st.session_state["role"]

# App Header
st.title("🇬🇭 EPA Ghana | PM₂.₅ Monitoring App")
st.info(f"👤 Logged in as: **{username}** (Role: {role})")

# Load data once
if "df" not in st.session_state:
    with st.spinner("🔄 Loading data..."):
        st.session_state.df = load_data_from_sheet(sheet)
        st.session_state.sheet = sheet
        st.session_state.spreadsheet = spreadsheet

# Role-based navigation
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

# Sidebar navigation
st.sidebar.title("📁 Navigation")
selected_page = st.sidebar.radio("Go to", pages)

# Show logout button
logout_button()

# Guide the user
st.success(f"✅ Use the sidebar to access: **{selected_page}**")
