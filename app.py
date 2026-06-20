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
MAX_HISTORY_TURNS = 3


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


def _build_history(messages: list, max_turns: int = MAX_HISTORY_TURNS):
    """
    Walk backwards through session messages and collect up to `max_turns`
    complete user/assistant pairs in chronological order.
    Returns a list of (user_text, assistant_text) tuples, or None if none yet.
    """
    pairs = []
    i = len(messages) - 1
    while i >= 1 and len(pairs) < max_turns:
        if messages[i]["role"] == "assistant" and messages[i - 1]["role"] == "user":
            pairs.append((messages[i - 1]["content"], messages[i]["content"]))
            i -= 2
        else:
            i -= 1
    pairs.reverse()
    return pairs if pairs else None


if "messages" not in st.session_state:
    st.session_state.messages = []

if "feedback" not in st.session_state:
    st.session_state.feedback = {}

if "ingested_pdfs" not in st.session_state:
    st.session_state.ingested_pdfs = set()

# Memory: last resolved topic for pronoun chaining ("that", "it")
if "last_resolved_topic" not in st.session_state:
    st.session_state.last_resolved_topic = None

# Memory: persisted bullet list from the most recent enumeration answer
# so ordinal follow-ups ("second one", "third one") always resolve against
# the ORIGINAL list, not the last single-topic answer.
if "reference_list" not in st.session_state:
    st.session_state.reference_list = None


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
        st.session_state.last_resolved_topic = None
        st.session_state.reference_list = None
        st.rerun()

    st.caption(
        "Answers are generated strictly from retrieved website content. "
        "If nothing relevant is found, the assistant will say so instead "
        "of guessing."
    )


# Input with PDF upload inside chat bar
pending = st.session_state.pop("pending", None)

chat = st.chat_input(
    "Ask about HBT Technology Services...",
    accept_file=True,
    file_type=["pdf"],
)

uploaded_pdf = chat.files[0] if chat and chat.files else None
user_input = chat.text if chat else None

if uploaded_pdf:
    if uploaded_pdf.name not in st.session_state.ingested_pdfs:
        from embeddings.pdf_ingestor import ingest_pdf
        with st.spinner(f"Processing {uploaded_pdf.name}..."):
            count = ingest_pdf(uploaded_pdf, uploaded_pdf.name)
        if count:
            st.session_state.ingested_pdfs.add(uploaded_pdf.name)
            st.toast(f"✅ Added {count} chunks from '{uploaded_pdf.name}'")
        else:
            st.toast("⚠️ Could not extract text from PDF.")
    else:
        st.toast(f"'{uploaded_pdf.name}' already ingested this session.")

user_input = user_input or pending

if user_input:
    history = _build_history(st.session_state.messages)

    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Searching knowledge base..."):
            result = ask_question_detailed(
                user_input,
                history=history,
                last_resolved_topic=st.session_state.last_resolved_topic,
                reference_list=st.session_state.reference_list,
            )
        st.write(result.answer)

        if result.answer != NOT_FOUND_MESSAGE:
            render_sources(result.sources)

    # Persist memory for next turn
    st.session_state.last_resolved_topic = result.resolved_topic
    st.session_state.reference_list = result.reference_list

    st.session_state.messages.append({
        "role": "assistant",
        "content": result.answer,
        "sources": result.sources,
    })
    st.rerun()