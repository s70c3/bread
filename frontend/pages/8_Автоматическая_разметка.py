import streamlit as st
from streamlit_drawable_canvas import st_canvas
import cv2
from PIL import Image
import requests

# Fetch the list of cameras
response = requests.get('http://backend:8000/camera')
if response.status_code == 200:
    sources_raw = response.json()
    sources = {camera['name']: camera['rtsp_stream'] for camera in sources_raw['cameras']}
    camera_ids = {camera['name']: camera['camera_id'] for camera in sources_raw['cameras']}
else:
    print('Не получается получить список камер. Проверьте доступ к серверу.')

# Fetch the list of bread products
response = requests.get('http://backend:8000/bread/')
if response.status_code == 200:
    breads = response.json()
    breads = {bread['name']: bread['product_id'] for bread in breads['breads']}
else:
    print('Не получается получить список хлебобулочных изделий. Проверьте доступ к серверу.')

# Let the user select a camera and a bread product
source_radio = st.radio("Выберите камеру", sources.keys())
bread_select = st.selectbox('Выберите хлебобулочное изделие', list(breads.keys()))

stream_address= str(sources.get(source_radio))

# Fetch the RTSP stream
stream = cv2.VideoCapture(stream_address)

# Capture a frame from the stream
ret, frame = stream.read()

# Convert the frame to RGB
frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
frame = cv2.resize(frame, (720, int(720*(9/16))))

st.markdown("Проверьте, что на конвейере выбранный тип продукции.")
st.image(frame)

# Send the data to the backend
if st.button('Подтвердить'):
    response = requests.post('http://backend:8543/label/', json={
        'camera_id': camera_ids[source_radio],
        'product_id': breads[bread_select],
        'name' : bread_select
    })
    if response.status_code == 200:
        st.write('Запрос на разметку отправлен успешно.')
    else:
        st.write('Не удалось отправить данные.')
        st.write(response.text)