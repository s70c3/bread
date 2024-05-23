import streamlit as st
import requests
from datetime import date, datetime

# Fetch the data
response = requests.get('http://backend:8000/bread/')
data = response.json()['breads']

# Display the data in a list
product_list = {bread['name']: bread['product_id'] for bread in data}
product_to_view = st.selectbox('Выберите продукт', list(product_list.keys()))

# Ask the user to select a date range
start_date = st.date_input('Начало периода', value=date.today())
end_date = st.date_input('Конец периода', value=date.today())

# Ask the user to select a time range
start_time = st.time_input('Start time', value=datetime.now().time())
end_time = st.time_input('End time', value=datetime.now().time())

# Combine date and time into datetime objects
start_datetime = datetime.combine(start_date, start_time)
end_datetime = datetime.combine(end_date, end_time)

# Send a GET request with the selected product ID and date range
if st.button('Просмотр'):
    response = requests.get(f'http://backend:8000/bread/count/{product_list[product_to_view]}?start_datetime={start_datetime.isoformat()}&end_datetime={end_datetime.isoformat()}')
    if response.status_code == 200:
        st.write(f'Количество продукта {product_to_view} с {start_datetime} по {end_datetime}: {response.json()}')
    else:
        st.write('Failed to fetch data')
        st.write(response.text)