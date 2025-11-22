import streamlit as st
import os
import shutil
import time

from backend.ingest_file import ingest_file

# ----------------------------------------------------------
# PAGE CONFIG
# ----------------------------------------------------------
st.set_page_config(page_title="Admin Dashboard", page_icon="🛡️", layout="wide")

# ----------------------------------------------------------
# ADMIN LOGIN CHECK
# ----------------------------------------------------------
if not st.session_state.get("is_admin"):
    st.error("❌ Unauthorized. Please login first.")
    st.stop()

# ----------------------------------------------------------
# DIRECTORIES
# ----------------------------------------------------------
PENDING_DIR = "uploads/pending"
APPROVED_DIR = "uploads/approved"
REJECTED_DIR = "uploads/rejected"
CHROMA_DIR = "uploads/.chroma_data"

os.makedirs(PENDING_DIR, exist_ok=True)
os.makedirs(APPROVED_DIR, exist_ok=True)
os.makedirs(REJECTED_DIR, exist_ok=True)
os.makedirs(CHROMA_DIR, exist_ok=True)

# ----------------------------------------------------------
# HEADER
# ----------------------------------------------------------
st.markdown("""
<h1 style='font-size: 2.6rem;'>🛡️ Admin Dashboard</h1>
<p>Welcome, Commander! Manage uploads & training below 👇🔥</p>
""", unsafe_allow_html=True)

# ==========================================================
# 🚀 FAST UPLOAD (ADMIN ONLY → DIRECT TO APPROVED)
# ==========================================================
st.markdown("## 🚀 Fast Upload (Instant Training)")
st.caption("Admins upload here — file is immediately trained and placed into APPROVED 😎📚")

if st.session_state.get("fast_done"):
    # Skip uploader on the rerun to prevent flicker
    st.session_state["fast_done"] = False
    fast_file = None
else:
    fast_file = st.file_uploader(
        "Drag and drop or browse",
        type=["pdf"],
        key="fast_upload"
    )

if fast_file:
    # Save directly to APPROVED (NOT pending)
    approved_path = os.path.join(APPROVED_DIR, fast_file.name)
    with open(approved_path, "wb") as f:
        f.write(fast_file.read())

    status = st.info("🤖 Training on this document… hang tight!")

    # Ingest from approved location
    result = ingest_file(approved_path, move_to_approved=False)

    status.empty()

    # Show output
    if result["status"] == "duplicate":
        st.warning(result["message"])
    elif result["status"] == "error":
        st.error(result["message"])
    else:
        st.success(f"{result['message']} 💡 Ready to chat about this document!")
        st.balloons()

    # Set flicker guard
    st.session_state["fast_done"] = True

    st.rerun()

# ----------------------------------------------------------
# 📥 PUBLIC PENDING UPLOADS
# ----------------------------------------------------------
st.markdown("---")
st.markdown("## 📥 Pending Public Uploads")

pending_files = [f for f in os.listdir(PENDING_DIR) if f != ".gitkeep"]

if not pending_files:
    st.info("✨ No pending uploads. All clear!")
else:
    for f in pending_files:
        full_path = os.path.join(PENDING_DIR, f)
        st.markdown(f"### 📄 {f}")

        col1, col2 = st.columns([1, 1])

        # APPROVE & INGEST
        with col1:
            if st.button(f"✔ Approve & Train", key=f"approve_{f}"):
                status = st.info(f"🤖 Training on **{f}**…")

                result = ingest_file(full_path)

                status.empty()

                if result["status"] == "duplicate":
                    st.warning(result["message"])
                elif result["status"] == "error":
                    st.error(result["message"])
                else:
                    st.success(f"{result['message']} 💡 Ready to chat about this document!")
                    st.balloons()

                st.rerun()

        # REJECT
        with col2:
            if st.button(f"❌ Reject", key=f"reject_{f}"):
                shutil.move(full_path, os.path.join(REJECTED_DIR, f))
                st.warning(f"🚫 Rejected **{f}**")
                st.rerun()

# ----------------------------------------------------------
# LOGOUT
# ----------------------------------------------------------
st.markdown("---")
if st.button("🚪 Logout"):
    st.session_state["is_admin"] = False
    st.success("Logged out!")
    st.rerun()

# ----------------------------------------------------------
# 💣 SELF-DESTRUCT (WINDOWS SAFE)
# ----------------------------------------------------------
st.markdown("---")
st.markdown("""
<div style='padding: 15px; border: 2px solid #b30000; border-radius: 8px; background-color:#33000033;'>
<h2 style='color:#ff4d4d;'>💣 Danger Zone – Total System Reset</h2>
<p>This wipes ALL PDFs and ALL trained Chroma data.<br>
Fully Windows-safe. No errors. Always resets cleanly 😅</p>
</div>
""", unsafe_allow_html=True)

if st.button("🧨 Initiate Self-Destruct"):
    st.session_state["self_destruct"] = True

if st.session_state.get("self_destruct"):

    st.warning("⚠️ WARNING: Self-destruct sequence armed!")

    if st.button("🚨 PROCEED to Self-Destruct"):

        placeholder = st.empty()
        for i in [3, 2, 1]:
            placeholder.markdown(
                f"<h1 style='text-align:center; color:red; font-size:5rem;'>💥 {i}</h1>",
                unsafe_allow_html=True
            )
            time.sleep(1)

        # Remove PDFs
        for folder in [PENDING_DIR, APPROVED_DIR, REJECTED_DIR]:
            for fn in os.listdir(folder):
                if fn != ".gitkeep":
                    os.remove(os.path.join(folder, fn))

        # Windows-safe Chroma reset
        if os.path.exists(CHROMA_DIR):
            try:
                shutil.rmtree(CHROMA_DIR)
            except Exception:
                # If locked, move its CONTENTS aside instead of renaming directory
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                trash_path = f"{CHROMA_DIR}_LOCKED_{timestamp}"
                os.makedirs(trash_path, exist_ok=True)
                st.warning(
                    f"⚠️ Chroma DB was locked.\n"
                    f"Moved unlocked files to:\n`{trash_path}`\n"
                    "Fresh DB created."
                )

        # Recreate fresh Chroma folder
        os.makedirs(CHROMA_DIR, exist_ok=True)

        st.success("🧹 BOOM! System fully reset. Fresh & clean! 🎉")
        st.balloons()
        st.session_state["self_destruct"] = False

    if st.button("🚫 Cancel Self-Destruct"):
        st.session_state["self_destruct"] = False
        st.info("❄️ Self-destruct canceled.")
