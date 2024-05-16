import streamlit as st
import requests
import base64

st.set_page_config(page_title="Добавить новый продукт", page_icon="📈")

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
        st.image(bytes_data)
        images_base64.append(base64_str)

    submit_button = st.form_submit_button(label='Submit')

if submit_button:
    # Send the images to FastAPI
    response = requests.post('http://backend:8000/bread/',
                             json={"name": text_input, "photos": images_base64})
    if response.status_code == 200:
        st.write('Images uploaded successfully')
    else:
        st.write('Failed to upload images')