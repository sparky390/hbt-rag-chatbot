import streamlit as st

from ui.chat_ui import render_chat


def main():
    st.set_page_config(page_title="HBT AI Knowledge Assistant", layout="wide")
    st.title("HBT AI Knowledge Assistant")
    render_chat()


if __name__ == "__main__":
    main()
