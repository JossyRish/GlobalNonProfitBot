import streamlit as st
import os
import time

# ----------------------------------------------------------
# Teen-Friendly, Fun Upload Page 🎉
# ----------------------------------------------------------

PENDING_DIR = "uploads/pending"
MAX_SIZE_MB = 5  # kids won't upload giant files… hopefully 😅

os.makedirs(PENDING_DIR, exist_ok=True)

st.set_page_config(page_title="Upload a PDF", page_icon="📄")

# ----------------------------------------------------------
# HEADER — FUN + PROFESSIONAL
# ----------------------------------------------------------
st.markdown("""
<div style="padding-top: 10px;"></div>
<h1 style='font-size: 2.8rem; display:flex; align-items:center; gap:10px'>
📄 Upload a PDF <span style='font-size:2rem'>✨</span>
</h1>

<p style='font-size:1.1rem; color:#ddd'>
Welcome to the <strong>STL Electives Training Portal</strong> —  
where *you* help power the AI chatbot! 💡🤖  
Drop your PDF and level up the bot’s knowledge. 🎮📚
</p>
""", unsafe_allow_html=True)

# ----------------------------------------------------------
# HOW IT WORKS – Fun checklist 🍀
# ----------------------------------------------------------
st.markdown("""
### 🧭 How This Works
- 🚀 **You upload a PDF** (electives, schedules, cheat sheets…)
- 📨 It goes into a **pending queue**
- 🛡️ Admin will **approve or reject** it
- 🤯 Once approved, it becomes part of the **chatbot's brain**

Think of it like feeding Kirby 🍓… but with *knowledge*!  
""")

# ----------------------------------------------------------
# FILE UPLOADER — Pretty & Friendly
# ----------------------------------------------------------
uploaded_file = st.file_uploader(
    "🎒 Drop a PDF here or click Browse (max 5MB)",
    type=["pdf"]
)

if uploaded_file:

    # 1. Safety: correct file type
    if not uploaded_file.name.lower().endswith(".pdf"):
        st.error("❌ Oops! Only PDF files allowed.")
        st.stop()

    # 2. Safety: size check
    size_mb = uploaded_file.size / (1024 * 1024)
    if size_mb > MAX_SIZE_MB:
        st.error(f"⚠️ File too big! Max allowed is {MAX_SIZE_MB} MB.")
        st.stop()

    # 3. Save file
    timestamp = int(time.time())
    safe_name = f"upload_{timestamp}.pdf"
    save_path = os.path.join(PENDING_DIR, safe_name)

    with open(save_path, "wb") as f:
        f.write(uploaded_file.read())

    # ----------------------------------------------------------
    # SUCCESS FEEDBACK — Fun + engaging 🎉
    # ----------------------------------------------------------
    st.success(f"🎉 Woohoo! Your file **{uploaded_file.name}** is now pending review!")
    st.balloons()

    st.info("""
    🧐 **What happens next?**  
    Sit tight! The Admin will check your upload and (most likely 😅) approve it.

    Once approved, your file becomes part of the AI's memory.  
    You're basically… **teaching a robot.** 🤓🤖💙
    """)

    st.markdown("<br>", unsafe_allow_html=True)
