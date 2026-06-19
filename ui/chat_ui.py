import streamlit as st


def render_chat():
    st.sidebar.header("Conversation")
    query = st.text_input("Ask a question about HBT services")
    if query:
        st.write("Searching knowledge base...")
        # TODO: connect to RAG chatbot
        st.write("You asked:", query)
