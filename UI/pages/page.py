import streamlit as st

st.set_page_config(page_title="Sidebar Navigation", page_icon="📂")

st.sidebar.title("Navigation")
page = st.sidebar.selectbox("Select a page:", ["Home", "About", "Contact"])

# Redirect to selected page
if page == "Home":
    st.switch_page("contact.py")
elif page == "About":
    st.switch_page("about.py")
elif page == "Contact":
    st.switch_page("contact.py")
