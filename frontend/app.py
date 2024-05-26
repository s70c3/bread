# Contents of ~/my_app/main_page.py
import streamlit as st
# Setting page layout
st.set_page_config(
    page_title="Запросы на подсчёт",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Python In-built packages
import requests

# External packages
import streamlit as st


# Main page heading
st.title("Запросы на подсчёт")
