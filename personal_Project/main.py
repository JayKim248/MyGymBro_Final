import streamlit as st

# Page configuration
st.set_page_config(
    page_title="MyGymBro - Redirecting...",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Redirect to home page
st.switch_page("pages/0_home.py")