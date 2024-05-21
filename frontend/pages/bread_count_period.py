import streamlit as st
import requests
from datetime import date

# Fetch the data
response = requests.get('http://backend:8000/bread/')
data = response.json()['breads']

# Display the data in a list
product_list = {bread['name']: bread['product_id'] for bread in data}
product_to_view = st.selectbox('Select a product', list(product_list.keys()))

# Ask the user to select a date range
start_date = st.date_input('Start date', value=date.today())
end_date = st.date_input('End date', value=date.today())

# Send a GET request with the selected product ID and date range
if st.button('View'):
    response = requests.get(f'http://backend:8000/bread/count/{product_list[product_to_view]}?start_date={start_date}&end_date={end_date}')
    if response.status_code == 200:
        st.write(f'Count of {product_to_view} from {start_date} to {end_date}: {response.json()}')
    else:
        st.write('Failed to fetch data')
        st.write(response.text)