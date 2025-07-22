import time
import streamlit as st

def stream_markdown(text, delay=0.05):
    """
    Stream markdown-formatted text line-by-line with animation.
    Supports lists, headings, bold, etc.
    """
    placeholder = st.empty()
    current_text = ""

    for line in text.splitlines():
        current_text += line + "\n"
        placeholder.markdown(current_text)
        time.sleep(delay)