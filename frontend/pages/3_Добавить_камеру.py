import streamlit as st
import requests
import base64

st.set_page_config(page_title="Добавить новую камеру", page_icon="📈")

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