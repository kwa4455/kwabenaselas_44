import streamlit as st
from utils import load_data_from_sheet, add_data, merge_start_stop,save_merged_data_to_sheet,sheet,spreadsheet

st.set_page_config(page_title="PM2.5 Monitoring App", layout="wide")
st.title("🌫️ PM2.5 Monitoring Dashboard")

st.markdown("""
Welcome to the PM2.5 Air Quality Monitoring Dashboard. Use the sidebar to navigate between:
- 📝 New data entry
- ✏️ Edit submitted records
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

# --- Sidebar with Developer Info and Logo ---
with st.sidebar:
    
    st.markdown("---")
    st.markdown("### 📞 For any Information, Please Contact")
    st.markdown("### 👤 The Developer")
    st.markdown("**Clement Mensah Ackaah**  \nEnvironmental Data Analyst")
    st.markdown("[📧 Email 1](mailto:clement.ackaah@epa.gov.gh) | [📧 Email 2](mailto:clementackaah70@gmail.com)")
    st.markdown("[🌐 Website](https://epa.gov)")

    st.markdown("---")
    

# --- Page Title ---
st.title("🇬🇭 EPA Ghana | PM₂.₅ Monitoring Data Entry")

if "df" not in st.session_state:
    df = load_data_from_sheet(sheet)
    st.session_state.df = df
    st.session_state.sheet = sheet
    st.session_state.spreadsheet = spreadsheet
