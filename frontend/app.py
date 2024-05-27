import streamlit as st
from pages.utils.password import check_password

def render_sidebar():
    """Render the sidebar only if the password is correct."""
    if st.session_state.get("password_correct", False):
        # Add your sidebar elements here
        pass

def render_main_content():
    """Render the main content only if the password is correct."""
    if st.session_state.get("password_correct", False):
        st.write("Добро пожаловать в систему подсчёта хлебобулочных изделий")

if not check_password():
    st.stop()  # Do not continue if check_password is not True.

render_sidebar()
render_main_content()