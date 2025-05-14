import streamlit as st
from utils import load_data_from_sheet, sheet, spreadsheet,login, logout_button


login()  # stops app until user logs in

# === After login, these will be safe ===
username = st.session_state["username"]
role = st.session_state["role"]


 === App Setup ===
st.set_page_config(page_title="PM₂.₅ Monitoring App", layout="wide")
st.title("🇬🇭 EPA Ghana | PM₂.₅ Monitoring App")
st.info(f"👤 Logged in as: **{username}** (Role: {role})")

# === Role-Based Navigation ===
if role == "admin":
    options = ["New Data Entry", "Edit Submitted Records", "Review & Merge"]
elif role == "editor":
    options = ["Edit Submitted Records", "Review & Merge"]
elif role == "collector":
    options = ["New Data Entry"]
else:
    st.error("❌ Invalid role.")
    st.stop()

# --- Custom CSS + Google Fonts ---
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto&display=swap');

        html, body, [class*="css"] {
            font-family: 'Roboto', sans-serif;
        }

        .stButton>button {
            background-color: #006400;
            color: white;
            font-weight: bold;
        }

        .stButton>button:hover {
            background-color: #004d00;
        }

        footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- Sidebar Info ---
with st.sidebar:
    st.markdown("### 📞 For Assistance Contact:")
    st.markdown("**👤 Clement Mensah Ackaah**  \nEnvironmental Data Analyst")
    st.markdown("[📧 clement.ackaah@epa.gov.gh](mailto:clement.ackaah@epa.gov.gh)")
    st.markdown("[📧 clementackaah70@gmail.com](mailto:clementackaah70@gmail.com)")
    st.markdown("[🌐 Visit EPA Website](https://epa.gov.gh)")
    st.markdown("---")

# --- Load Data Once and Store in Session ---
if "df" not in st.session_state:
    with st.spinner("Loading data from Google Sheets..."):
        st.session_state.df = load_data_from_sheet(sheet)
        st.session_state.sheet = sheet 
        st.session_state.spreadsheet = spreadsheet


st.sidebar.title("📁 Navigation")
selected_page = st.sidebar.radio("Go to", options)

logout_button()
