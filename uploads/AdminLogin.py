import streamlit as st

st.set_page_config(page_title="Admin Login", page_icon="🔐")

ADMIN_PASSWORD = "admin123"  # change this any time

if "is_admin" not in st.session_state:
    st.session_state.is_admin = False

st.title("🔐 Admin Login")

st.write("""
Welcome to the **AI Secret Base** 😎  
Enter your super-secret password to unlock the control center.
""")

pw = st.text_input("Password", type="password")

if st.button("Login 🚀"):
    if pw == ADMIN_PASSWORD:
        st.session_state.is_admin = True
        st.success("Access Granted! 🛡️ Loading Admin Dashboard…")
        st.switch_page("pages/admin/Dashboard.py")
    else:
        st.error("❌ Wrong passcode. Try again.")
