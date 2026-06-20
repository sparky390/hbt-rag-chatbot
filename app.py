import json
import os
import streamlit as st
from rag.chatbot import ask_question_detailed, NOT_FOUND_MESSAGE, warmup

st.set_page_config(
    page_title="HBT AI Knowledge Assistant",
    page_icon="🤖",
    layout="centered",
)

st.title("🤖 HBT AI Knowledge Assistant")
st.caption("Answers grounded in HBT Technology Services website content.")

warmup()

FEEDBACK_FILE = "data/feedback.json"


def save_feedback(question: str, answer: str, rating: str):
    os.makedirs("data", exist_ok=True)
    existing = []
    if os.path.exists(FEEDBACK_FILE):
        with open(FEEDBACK_FILE, "r", encoding="utf-8") as f:
            existing = json.load(f)
    existing.append({
        "question": question,
        "answer": answer,
        "feedback": rating,
    })
    with open(FEEDBACK_FILE, "w", encoding="utf-8") as f:
        json.dump(existing, f, indent=4, ensure_ascii=False)


if "messages" not in st.session_state:
    st.session_state.messages = []

if "feedback" not in st.session_state:
    st.session_state.feedback = {}


def render_sources(sources):
    if not sources:
        return
    with st.expander(f"📄 Sources ({len(sources)})", expanded=False):
        for s in sources:
            heading = f" — *{s.heading_path}*" if s.heading_path else ""
            st.markdown(
                f"- **{s.doc_title}**{heading}  \n"
                f"  `{s.source_file}` · similarity {s.similarity:.2f}"
            )


def render_feedback(i: int, question: str, answer: str):
    col1, col2, col3 = st.columns([1, 1, 8])
    with col1:
        if st.button("👍", key=f"up_{i}"):
            st.session_state.feedback[i] = "helpful"
            save_feedback(question, answer, "helpful")
    with col2:
        if st.button("👎", key=f"dn_{i}"):
            st.session_state.feedback[i] = "not helpful"
            save_feedback(question, answer, "not helpful")
    if i in st.session_state.feedback:
        st.caption(f"Marked as: {st.session_state.feedback[i]}")


# Render previous messages
for i, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if msg["role"] == "assistant":
            render_sources(msg.get("sources", []))

    if msg["role"] == "assistant":
        question = ""
        if i > 0 and st.session_state.messages[i - 1]["role"] == "user":
            question = st.session_state.messages[i - 1]["content"]
        render_feedback(i, question, msg["content"])


# Sidebar
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

    st.divider()
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.feedback = {}
        st.rerun()

    st.divider()
    st.caption(
        "Answers are generated strictly from retrieved website content. "
        "If nothing relevant is found, the assistant will say so instead "
        "of guessing."
    )


# Input
pending = st.session_state.pop("pending", None)
user_input = st.chat_input("Ask about HBT Technology Services...") or pending

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Searching knowledge base..."):
            result = ask_question_detailed(user_input)
        st.write(result.answer)

        if result.answer != NOT_FOUND_MESSAGE:
            render_sources(result.sources)

    st.session_state.messages.append({
        "role": "assistant",
        "content": result.answer,
        "sources": result.sources,
    })
    st.rerun()