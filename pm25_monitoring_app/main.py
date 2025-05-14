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
    with st.spinner("Loading data from Google Sheets..."):
        st.session_state.df = load_data_from_sheet(sheet)
        st.session_state.sheet = sheet 
        st.session_state.spreadsheet = spreadsheet

# --- Sidebar Navigation ---
page = st.sidebar.radio(
    "Navigate",
    options=["New Data Entry", "Edit Submitted Records", "Review & Merge Data"]
)

# --- New Data Entry Page ---
if page == "New Data Entry":
    st.subheader("📝 New Data Entry")
    st.markdown("Fill out the form to add new air quality monitoring data.")
    # Implement the form for new data entry (You can define the fields you want to capture)

# --- Edit Submitted Records Page ---
elif page == "Edit Submitted Records":
    st.subheader("✏️ Edit Submitted Records")
    st.markdown("Modify records that have already been submitted.")
    # Implement the functionality for editing submitted records

# --- Review & Merge Data Page ---
elif page == "Review & Merge Data":
    st.subheader("📊 Review & Merge Data")
    st.markdown("Review submitted records and merge START and STOP records.")
    # Display the data from session_state and allow the user to filter, view and merge records
    if "df" in st.session_state:
        df = st.session_state.df
        st.dataframe(df)  # Show the records in a table (with filtering and merging options)

# --- Logout Button ---
if st.button("Logout"):
    st.session_state.clear()
    st.experimental_rerun()
