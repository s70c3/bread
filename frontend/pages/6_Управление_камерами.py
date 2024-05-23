import streamlit as st
import requests
import pandas as pd

# Fetch the data
response = requests.get('http://backend:8543/camera/')
data = response.json()['cameras']

if data:
    # Convert the data to a pandas DataFrame
    df = pd.DataFrame(data)

    # Display the data in a table
    st.table(df)

    # Ask the user to select a row to edit or delete
    row_to_edit = st.number_input('Введите номер изменяемой камеры', min_value=0, max_value=len(df)-1)

    # Ask the user if they want to edit or delete the selected row
    action = st.selectbox('Вы хотите изменить или удалить камеру?', options=['Изменить', 'Удалить'])

    if action == 'Изменить':
        # Display a form for the user to edit the data
        with st.form(key='edit_form'):
            new_data = {}
            for column in df.columns:
                new_data[column] = st.text_input(f'Введите новые значения {column}', value=df.loc[row_to_edit, column])
            submit_button = st.form_submit_button(label='Подтвердить')

        if submit_button:
            # Send a PUT request with the new data
            response = requests.put(f'http://backend:8543/camera/{df.loc[row_to_edit, "camera_id"]}', json=new_data)
            if response.status_code == 200:
                st.write('Данные успешно обновлены')
            else:
                st.write('Не удалось обновить данные')
                st.write('Данные ошибки:')
                st.write(response.text)

    elif action == 'Удалить':
        # Confirm the deletion
        if st.button('Подтвердить удаление'):
            # Send a DELETE request
            response = requests.delete(f'http://backend:8543/camera/{df.loc[row_to_edit, "camera_id"]}')
            if response.status_code == 200:
                st.write('Дата успешно обновлены')
            else:
                st.write('Не удалось удалить')
                st.write('Данные ошибки:')
                st.write(response.text)
else:
    st.write('Камер в базе нет.')


st.markdown("Добавление новой камеры")
st.sidebar.header("Добавление новой камеры")

with st.form(key="bread_form"):
    text_input = st.text_input("Введите название камеры")

    address = st.text_input("Введите rtsp-адрес камеры")

    description = st.text_input("Введите описание камеры")

    submit_button = st.form_submit_button(label='Отправить')


if submit_button:
    # Send the images to FastAPI
    response = requests.post('http://backend:8543/camera/',
                             json={"name": text_input, "rtsp_stream" : address, "description" : description})
    if response.status_code == 200:
        st.write('Изображения загружены успешно.')
    else:
        st.write('Не удалось загрузить изображения.')