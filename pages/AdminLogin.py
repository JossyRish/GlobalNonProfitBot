import streamlit as st

st.set_page_config(page_title="Admin Login")

# Initialize session flag
if "is_admin" not in st.session_state:
    st.session_state["is_admin"] = False

st.title("🔐 Admin Login")
st.write("This page is for administrators only.")

ADMIN_PASSWORD = "1234"  # demo password


# Handle login button
def handle_login():
    entered = st.session_state.get("admin_password", "")
    if entered == ADMIN_PASSWORD:
        st.session_state["is_admin"] = True
        st.session_state["login_success"] = True  # set flag
    else:
        st.session_state["login_success"] = False


# Login UI
st.text_input(
    "Enter Admin Password:",
    type="password",
    key="admin_password",
)

st.button("Login", on_click=handle_login)

# ---- Redirect happens OUTSIDE callback ----
if st.session_state.get("login_success"):
    st.success("Login successful!")
    st.switch_page("pages/Dashboard.py")
