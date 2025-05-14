import streamlit as st
from utils import load_data_from_sheet, sheet, spreadsheet

# --- Page Setup ---
st.set_page_config(page_title="PM₂.₅ Monitoring Data Entry App", layout="wide")

# --- Page Title ---
st.title("🇬🇭 EPA Ghana | PM₂.₅ Monitoring Data Entry App")

st.markdown("""
Welcome to the PM₂.₅ Air Quality Monitoring Data Entry Tool.  
Use the sidebar to navigate between:
- 📝 New data entry
- ✏️ Edit submitted records
- 📊 Review & merge data
""")

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
    st.session_state.df = load_data_from_sheet(sheet)
    st.session_state.sheet = sheet
    st.session_state.spreadsheet = spreadsheet
