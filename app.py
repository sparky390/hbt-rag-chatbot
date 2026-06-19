import streamlit as st
from rag.chatbot import ask_question

st.set_page_config(
    page_title="HBT AI Knowledge Assistant",
    page_icon="🤖",
    layout="centered",
)

st.title("🤖 HBT AI Knowledge Assistant")
st.caption("Answers grounded in HBT Technology Services website content.")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

with st.sidebar:
    st.header("Sample Questions")
    samples = [
        "What services does HBT Technology Services offer?",
        "What is Data as a Service at HBT?",
        "What automation solutions does HBT provide?",
        "What is HBT's engineering services capability?",
        "What does HBT do for technical documentation?",
        "What is strategic sourcing at HBT?",
    ]
    for q in samples:
        if st.button(q, use_container_width=True):
            st.session_state["pending"] = q

pending = st.session_state.pop("pending", None)
user_input = st.chat_input("Ask about HBT Technology Services...") or pending

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Searching knowledge base..."):
            answer = ask_question(user_input)
        st.write(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})