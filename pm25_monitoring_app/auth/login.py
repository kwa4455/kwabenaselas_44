# 📁 auth/login.py
import streamlit as st
from supabase_client import supabase
from auth.utils import check_password
from postgrest import APIError

def login_user():
    st.title("🔐 Login")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        try:
            auth_response = supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })

            session = auth_response.session
            user = auth_response.user

            if not session:
                st.error("❌ Invalid credentials.")
                return None

            # Fetch profile from your `profiles` table
            profile_resp = supabase.table("profiles").select("*").eq("id", user.id).single().execute()
            profile = profile_resp.data

            if not profile["is_approved"]:
                st.warning("⏳ Awaiting admin approval.")
                return None

            # Save session state
            st.session_state.logged_in = True
            st.session_state.username = profile["email"]
            st.session_state.role = profile["role"]
            st.session_state.user_id = user.id

            st.success("✅ Login successful")
            return profile

        except Exception as e:
            st.error(f"Login failed: {e}")
            return None
