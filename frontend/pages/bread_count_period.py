import streamlit as st
import requests
from datetime import date

# Fetch the data
response = requests.get('http://backend:8000/bread/')
data = response.json()['breads']

# Display the data in a list
product_list = {bread['name']: bread['product_id'] for bread in data}
product_to_view = st.selectbox('Выберите продукт', list(product_list.keys()))

# Ask the user to select a date range
start_date = st.date_input('Начало периода', value=date.today())
end_date = st.date_input('Конец периода', value=date.today())

# Send a GET request with the selected product ID and date range
if st.button('Просмотр'):
    response = requests.get(f'http://backend:8000/bread/count/{product_list[product_to_view]}?start_date={start_date}&end_date={end_date}')
    if response.status_code == 200:
        st.write(f'Количество продукта {product_to_view} с {start_date} по {end_date}: {response.json()}')
    else:
        st.write('Failed to fetch data')
        st.write(response.text)