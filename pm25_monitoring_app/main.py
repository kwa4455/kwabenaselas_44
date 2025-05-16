import streamlit as st
from utils import login, load_data_from_sheet, sheet, spreadsheet, logout_button

# Login or stop if not authenticated
login()

# Now safe to access session state
username = st.session_state["username"]
role = st.session_state["role"]
st.set_page_config(page_title="PM₂.₅ Monitoring App", layout="wide")

st.title("🇬🇭 EPA Ghana | PM₂.₅ Monitoring App")
st.info(f"👤 Logged in as: **{username}** (Role: {role})")

# Load data once
if "df" not in st.session_state:
    with st.spinner("Loading data..."):
        st.session_state.df = load_data_from_sheet(sheet)
        st.session_state.sheet = sheet
        st.session_state.spreadsheet = spreadsheet

# Show navigation based on role
if role == "admin":
    pages = ["Data Entry", "Edit Records", "Review"]
elif role == "editor":
    pages = ["Edit Records", "Review "]
elif role == "viewer":
    pages = ["Review & Merge"]
elif role == "collector":
    pages = ["Data Entry", "Edit Records"]
else:
    st.error("❌ Invalid role.")
    st.stop()

# Sidebar navigation
st.sidebar.title("📁 Navigation")
selected_page = st.sidebar.radio("Go to", pages)

logout_button()

# Optional: Inform user where to navigate
st.success(f"✅ Please use the sidebar to go to: **{selected_page}**")
