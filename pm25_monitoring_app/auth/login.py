# 📁 auth/login.py
import streamlit as st
from supabase_client import supabase
from auth.utils import check_password


def login_user():
    st.title("🔐 Login")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        response = supabase.table("users").select("*").eq("email", email).single().execute()
        user = response.data

        if user and check_password(password, user["password_hash"]):
            if not user["is_approved"]:
                st.warning("⏳ Awaiting admin approval.")
                return None
            st.success("✅ Login successful")
            return user
        else:
            st.error("❌ Invalid credentials")
            return None
    return None
