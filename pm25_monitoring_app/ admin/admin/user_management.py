import streamlit as st
from supabase import create_client
from dotenv import load_dotenv
import os
from bcrypt import hashpw, gensalt

# Load credentials
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def require_admin():
    if "role" not in st.session_state or st.session_state["role"] != "admin":
        st.error("🚫 You must be an admin to access this page.")
        st.stop()

def admin_panel():
    require_admin()
    st.title("👨‍💼 Admin Panel - User Management")

    tabs = st.tabs(["🕒 Pending Approvals", "✅ Approved Users", "➕ Add New User"])

    # Pending Approvals
    with tabs[0]:
        st.subheader("🕒 Pending User Registrations")
        pending = supabase.table("users").select("*").eq("is_approved", False).execute().data

        if not pending:
            st.info("🎉 No pending registrations.")
        else:
            for user in pending:
                with st.expander(f"{user['email']} - {user['role']}"):
                    st.write(user)
                    col1, col2 = st.columns(2)
                    if col1.button(f"✅ Approve {user['email']}", key=f"approve_{user['id']}"):
                        supabase.table("users").update({"is_approved": True}).eq("id", user["id"]).execute()
                        st.success("✅ Approved")
                        st.rerun()
                    if col2.button(f"❌ Delete {user['email']}", key=f"reject_{user['id']}"):
                        supabase.table("users").delete().eq("id", user["id"]).execute()
                        st.warning("🗑️ Deleted")
                        st.rerun()

    # Approved Users
    with tabs[1]:
        st.subheader("✅ Approved Users")
        approved = supabase.table("users").select("*").eq("is_approved", True).execute().data

        for user in approved:
            with st.expander(f"{user['email']} - Role: {user['role']}"):
                new_role = st.selectbox("Change role", ["admin", "editor", "viewer", "collector"],
                                        index=["admin", "editor", "viewer", "collector"].index(user["role"]),
                                        key=f"role_{user['id']}")
                if st.button("Update Role", key=f"update_{user['id']}"):
                    supabase.table("users").update({"role": new_role}).eq("id", user["id"]).execute()
                    st.success("🔄 Role updated")
                    st.rerun()

    # Add New User
    with tabs[2]:
        st.subheader("➕ Manually Add New User")
        new_email = st.text_input("Email")
        new_username = st.text_input("Username")
        new_password = st.text_input("Password", type="password")
        new_role = st.selectbox("Role", ["admin", "editor", "viewer", "collector"])

        if st.button("Create User"):
            if new_email and new_password and new_username:
                hashed_pw = hashpw(new_password.encode(), gensalt()).decode()

                result = supabase.table("users").insert({
                    "email": new_email,
                    "username": new_username,
                    "password_hash": hashed_pw,
                    "role": new_role,
                    "is_approved": True
                }).execute()

                if result.data:
                    st.success("✅ User added successfully")
                    st.rerun()
                else:
                    st.error("❌ Failed to create user")
            else:
                st.warning("⚠️ Fill in all fields")
