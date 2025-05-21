import streamlit as st
import bcrypt
from supabase_client import supabase

def register_user():
    st.title("📝 Register")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    confirm = st.text_input("Confirm Password", type="password")
    role = st.selectbox("Select Role", ["collector", "editor", "viewer"])

    if st.button("Register"):
        if password != confirm:
            st.error("❌ Passwords do not match.")
            return

        try:
            # Step 1: Create Auth user
            auth_response = supabase.auth.sign_up({
                "email": email,
                "password": password
            })

            user = auth_response.user
            if not user:
                st.error("Registration failed. User not created.")
                return

            # Step 2: Insert into `profiles`
            supabase.table("profiles").insert({
                "id": user.id,
                "email": email,
                "role": role,
                "is_approved": False  # default: waiting for admin approval
            }).execute()

            st.success("✅ Registered successfully. Awaiting admin approval.")

        except Exception as e:
            st.error(f"❌ Error: {e}")

