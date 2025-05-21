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
        if not email or not password:
            st.warning("⚠️ Please enter both email and password.")
            return None

        try:
            response = supabase.table("users").select("*").eq("email", email).single().execute()
            user = response.data

            if user and check_password(password, user["password_hash"]):
                if not user["is_approved"]:
                    st.warning("⏳ Awaiting admin approval.")
                    return None
                st.success("✅ Login successful")
                return user
            else:
                st.error("❌ Invalid email or password")
                return None

        except APIError as e:
            # Print full Supabase error
            error_details = e.args[0] if e.args else "Unknown error"
            st.error("❌ Supabase error during login")
            st.code(str(error_details), language="json")
            return None

    return None
