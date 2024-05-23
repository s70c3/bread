import streamlit as st
import requests
import base64
from PIL import Image
from io import BytesIO

# Fetch the data
response = requests.get('http://backend:8543/bread/')
data = response.json()['breads']

if data:
    # Display the data in a list
    for i, bread in enumerate(data):
        st.write(f"{i}. {bread['name']}")
        img_data = base64.b64decode(bread['photos'])
        img = Image.open(BytesIO(img_data))
        st.image(img)


    # Ask the user to select a product to edit or delete
    product_to_edit = st.number_input('Введите номер продукта для обновления или удаления', min_value=0, max_value=len(data)-1)

    # Ask the user if they want to edit or delete the selected product
    action = st.selectbox('Вы хотите изменить или удалить это продукт?', options=['Изменить', 'Удалить'])

    if action == 'Изменить':
        # Display a form for the user to edit the data
        with st.form(key='edit_form'):
            new_name = st.text_input('Введите новое название', value=data[product_to_edit]['name'])
            new_photos = st.file_uploader("Загрузите новые фотографии", accept_multiple_files=True)
            new_photos_base64 = [base64.b64encode(photo.read()).decode() for photo in new_photos]
            submit_button = st.form_submit_button(label='Подтвердить')

        if submit_button:
            # Send a PUT request with the new data
            response = requests.put(f'http://backend:8543/bread/{data[product_to_edit]["product_id"]}', json={"name": new_name, "photos": new_photos_base64})
            if response.status_code == 200:
                st.write('Данные успешно обновлены.')
            else:
                st.write('Не удалось обновить продукт.')
                st.write(response.text)

    elif action == 'Удалить':
        # Confirm the deletion
        if st.button('Подтвердите удаление'):
            # Send a DELETE request
            response = requests.delete(f'http://backend:8543/bread/{data[product_to_edit]["product_id"]}')
            if response.status_code == 200:
                st.write('Продукт успешно удален')
            else:
                st.write('Не удалось удалить продукт')
                st.write(response.text)
else:
    st.write('Продукты в базе нет.')



st.markdown("Добавить нового продукта")
st.sidebar.header("Добавление нового продукта")

with st.form(key="bread_form"):
    text_input = st.text_input("Введите название продукта")

    uploaded_files = st.file_uploader("Выберите изображения", accept_multiple_files=True)

    # Convert the images to base64
    images_base64 = []
    for uploaded_file in uploaded_files:
        bytes_data = uploaded_file.read()
        base64_str = base64.b64encode(bytes_data).decode()
        # st.image(bytes_data)
        images_base64.append(base64_str)

    submit_button = st.form_submit_button(label='Подтвердить')

if submit_button:
    print(images_base64)
    # Send the images to FastAPI
    response = requests.post('http://backend:8543/bread/',
                             json={"name": text_input, "photos": images_base64})
    if response.status_code == 200:
        st.write('Изображения успешно загружены')
    else:
        st.write('Не удалось загрузить изображения')
        print(response.status_code)
        print(response.text)