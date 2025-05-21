import streamlit as st

def logout_user():
    if st.button("🔓 Logout"):
        # Clear session state variables
        st.session_state.logged_in = False
        st.session_state.pop("username", None)
        st.session_state.pop("role", None)
        st.session_state.pop("email", None)
        st.success("✅ You have been logged out.")
        st.experimental_rerun()
