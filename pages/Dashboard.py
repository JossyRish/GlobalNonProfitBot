import streamlit as st
import os
import shutil
import time
import random

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
UPLOADS_DIR = "uploads"

os.makedirs(PENDING_DIR, exist_ok=True)
os.makedirs(APPROVED_DIR, exist_ok=True)
os.makedirs(REJECTED_DIR, exist_ok=True)
os.makedirs(CHROMA_DIR, exist_ok=True)

# APPROVE STATE (store filename only)
if "approve_file" not in st.session_state:
    st.session_state.approve_file = None

# FAST UPLOAD flicker guard
if "fast_done" not in st.session_state:
    st.session_state.fast_done = False


# ----------------------------------------------------------
# 🔥 FUN TEEN-SWAG INGEST WRAPPER (Gen-Z vibe)
# ----------------------------------------------------------
def run_ingest_with_fun(pdf_path: str, *, move_to_approved: bool = True, label_name: str = ""):
    """
    Runs ingest_file with:
      ✅ Gen-Z teen swag animated progress
      ✅ Live status chatter
      ✅ Random emojis
      ✅ Toasts + Balloons on success
    Cloud-safe: animation first, then real ingest.
    """
    emoji_pool = ["🤖", "🔥", "✨", "😎", "🚀", "🧠", "📚", "⚡", "🎮", "💅", "🥳", "🫶"]
    def hype(msg):  # sprinkle random emoji
        return f"{random.choice(emoji_pool)} {msg} {random.choice(emoji_pool)}"

    hype_lines = [
        hype("Yo this PDF thick 😅 lemme slice it up real quick…"),
        hype("Scanning pages like a pro…"),
        hype("Breaking text into smart chunks…"),
        hype("Feeding my brain fresh knowledge…"),
        hype("Slaying these embeddings, queen 💅"),
        hype("Saving to my memory vault…"),
        hype("Almost done leveling up…"),
    ]

    # little live “chat” feel
    chatter_box = st.empty()
    progress = st.progress(0, hype_lines[0])

    # warmup animation (keeps it fun)
    for i, msg in enumerate(hype_lines):
        chatter_box.markdown(
            f"**{msg}**",
            unsafe_allow_html=True
        )
        progress.progress((i + 1) / len(hype_lines), msg)
        time.sleep(0.55)

    # real ingest
    chatter_box.markdown("**🧠 Now doing the REAL training… don’t blink 😤**")
    result = ingest_file(pdf_path, move_to_approved=move_to_approved)

    progress.empty()
    chatter_box.empty()

    # outcome UI
    if result["status"] == "duplicate":
        st.warning(result["message"])
        st.toast("😅 Already learned this one. Great minds think alike!", icon="📄")

    elif result["status"] == "error":
        st.error(result["message"])
        st.toast("💥 Oops. That one didn’t go through.", icon="⚠️")

    else:
        st.success(f"{result['message']} 💡 I’m smarter now FR FR 🤓🔥")
        st.toast("🎉 Training complete! Level up unlocked.", icon="🚀")
        st.balloons()

    return result


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

if st.session_state.fast_done:
    st.session_state.fast_done = False
    fast_file = None
else:
    fast_file = st.file_uploader(
        "Drag and drop or browse",
        type=["pdf"],
        key="fast_upload"
    )

if fast_file:
    approved_path = os.path.join(APPROVED_DIR, fast_file.name)
    with open(approved_path, "wb") as f:
        f.write(fast_file.read())

    run_ingest_with_fun(
        approved_path,
        move_to_approved=False,
        label_name=fast_file.name
    )

    st.session_state.fast_done = True
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
        st.markdown(f"### 📄 {f}")

        col1, col2 = st.columns([1, 1])

        # APPROVE BUTTON — triggers session state
        with col1:
            if st.button("✔ Approve & Train", key=f"approve_{f}"):
                st.session_state.approve_file = f
                st.rerun()

        # REJECT BUTTON
        with col2:
            if st.button("❌ Reject", key=f"reject_{f}"):
                shutil.move(
                    os.path.join(PENDING_DIR, f),
                    os.path.join(REJECTED_DIR, f)
                )
                st.warning(f"🚫 Rejected **{f}**")
                st.toast("Yeeted to Rejected 🗑️", icon="😈")
                st.rerun()

        # ------------------------------------------------------
        # APPROVE PROCESS (runs after rerun)
        # ------------------------------------------------------
        if st.session_state.approve_file == f:
            full_path = os.path.join(PENDING_DIR, f)

            run_ingest_with_fun(
                full_path,
                move_to_approved=True,
                label_name=f
            )

            st.session_state.approve_file = None
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
# 💣 SELF-DESTRUCT (WINDOWS + CLOUD SAFE)
# ----------------------------------------------------------
st.markdown("---")
st.markdown("""
<div style='padding: 15px; border: 2px solid #b30000; border-radius: 8px; background-color:#33000033;'>
<h2 style='color:#ff4d4d;'>💣 Danger Zone – Total System Reset</h2>
<p>This wipes ALL PDFs and ALL trained Chroma data.<br>
Fully Windows-safe. Cloud-safe. Always resets cleanly 😅</p>
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
                    try:
                        os.remove(os.path.join(folder, fn))
                    except:
                        pass

        # -------------------------------
        # 💾 Chroma DB reset (HARD SAFE)
        # -------------------------------
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        trash_path = f"{CHROMA_DIR}_LOCKED_{timestamp}"

        if os.path.exists(CHROMA_DIR):
            try:
                shutil.rmtree(CHROMA_DIR)
            except Exception:
                try:
                    os.rename(CHROMA_DIR, trash_path)
                    st.warning(
                        f"⚠️ Chroma was locked.\nMoved DB to:\n`{trash_path}`\nFresh DB created."
                    )
                except Exception:
                    for root, dirs, files in os.walk(CHROMA_DIR, topdown=False):
                        for name in files:
                            try:
                                os.remove(os.path.join(root, name))
                            except:
                                pass
                        for name in dirs:
                            try:
                                os.rmdir(os.path.join(root, name))
                            except:
                                pass

        # Recreate clean Chroma DB folder
        os.makedirs(CHROMA_DIR, exist_ok=True)

        # Clean up leftover Chroma LOCKED folders
        for fn in os.listdir(UPLOADS_DIR):
            if fn.startswith(".chroma_data_LOCKED_"):
                shutil.rmtree(os.path.join(UPLOADS_DIR, fn), ignore_errors=True)

        st.success("🧹 BOOM! System fully reset. Fresh & clean! 🎉")
        st.toast("Everything reset. New game started 🎮", icon="✨")
        st.balloons()
        st.session_state["self_destruct"] = False

    if st.button("🚫 Cancel Self-Destruct"):
        st.session_state["self_destruct"] = False
        st.info("❄️ Self-destruct canceled.")
