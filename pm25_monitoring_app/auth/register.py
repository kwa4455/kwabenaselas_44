import streamlit as st
import bcrypt
from supabase_client import supabase

def register_user():
    st.title("📝 Register for EPA Ghana | Field Data App")

    username = st.text_input("Username")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")
    role = st.selectbox("Role", ["collector", "editor", "viewer"])  # Admins are added manually

    if st.button("Register"):
        if not username or not email or not password:
            st.error("Please fill all fields.")
            return

        if password != confirm_password:
            st.error("Passwords do not match.")
            return

        # Check if user already exists
        existing_user = supabase.table("users").select("email", "username").eq("email", email).execute()
        if existing_user.data:
            st.error("User with this email already exists.")
            return

        # Hash the password
        hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

        # Insert into Supabase
        response = supabase.table("users").insert({
            "username": username,
            "email": email,
            "role": role,
            "password_hash": hashed_pw,
            "is_approved": False  # Admin must approve
        }).execute()

        if response.status_code == 201:
            st.success("✅ Registration successful! Awaiting admin approval.")
        else:
            st.error(f"❌ Registration failed: {response.error_message if hasattr(response, 'error_message') else 'Unknown error.'}")
