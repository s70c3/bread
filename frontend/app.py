# Contents of ~/my_app/main_page.py
import streamlit as st
# Setting page layout
st.set_page_config(
    page_title="Запросы на подсчёт",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("# Главная страница")
# Python In-built packages
import requests

# External packages
import streamlit as st


# Main page heading
st.title("Запросы на подсчёт")

# Make a GET request to the /count/ endpoint
response = requests.get("http://localhost:8000/count/")

# Check if the request was successful
if response.status_code == 200:
    # Get the counting requests from the response
    counting_requests = response.json()

    # Display the counting requests in a table
    st.table(counting_requests)
else:
    st.error("Failed to get counting requests")