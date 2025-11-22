import streamlit as st
import os

# ----------------------------------------------------------
# Streamlit Page Setup
# ----------------------------------------------------------
st.set_page_config(
    page_title="STL for STL – AI Learning Hub",
    page_icon="💎",
    layout="wide"
)

# ----------------------------------------------------------
# ROUTING: Show admin page when URL contains ?admin=true
# ----------------------------------------------------------
params = st.query_params   # modern API

if str(params.get("admin", "false")).lower() == "true":
    # Import the admin renderer from /admin/admin.py
    from admin.admin import render_admin_page
    render_admin_page()
    st.stop()


# ----------------------------------------------------------
# MAIN HOME PAGE CONTENT (Only shows when NOT calling admin)
# ----------------------------------------------------------

st.title("STL for STL – AI Learning Hub 💎")

st.write("### Welcome to the STL for STL AI Learning Hub!")

st.markdown(
    """
    This app demonstrates how a simple document-powered AI system works from end to end.

    ### **What this system does:**
    - Accepts **PDF uploads** from any user  
    - Stores uploads in a **pending review queue**  
    - Allows an **admin to approve or reject** each upload  
    - Automatically **ingests approved PDFs** into the AI knowledge base  
    - The chatbot can answer questions using all approved documents  
    - It also shows the **exact source PDF chunks** used in answers  
    - Students get to learn how document-powered AI actually works  
    """
)

st.info("Use the sidebar to navigate between Upload and Chatbot pages.")
