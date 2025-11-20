# --- app.py ---
import streamlit as st
from chatbot import ask_bot

st.set_page_config(page_title="Global Nonprofit Chatbot", page_icon="💬")

st.title("🌍 Global Nonprofit Chatbot")
st.write("Ask questions about your nonprofit mission, and the bot will respond.")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input
if user_input := st.chat_input("Type your message..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = ask_bot(user_input)
            st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})
