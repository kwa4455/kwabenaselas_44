import streamlit as st
import os
import streamlit as st
from supabase_client import supabas

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
    st.header("⚙️ Admin Panel")

    with st.expander("📝 Pending User Approvals"):
        try:
            response = supabase.table("profiles").select("*").eq("is_approved", False).execute()
            pending_users = response.data

            if not pending_users:
                st.info("✅ No users pending approval.")
            else:
                for user in pending_users:
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(f"**{user['email']}** - Role: `{user['role']}`")
                    with col2:
                        if st.button("Approve", key=user['id']):
                            supabase.table("profiles").update({"is_approved": True}).eq("id", user['id']).execute()
                            st.success(f"✅ Approved {user['email']}")
                            st.experimental_rerun()

        except Exception as e:
            st.error(f"Error loading users: {e}")
