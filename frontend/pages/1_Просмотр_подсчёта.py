# Python In-built packages
from pathlib import Path
import PIL
import cv2

# External packages
import streamlit as st

# Local Modules
import pages.utils.helper as helper
import pages.utils.settings as settings
from ultralytics import YOLO

# Setting page layout
st.set_page_config(
    page_title="Детекция хлебобулочных изделий в реальном времени",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Main page heading
st.title("Детекция хлебобулочных изделий в реальном времени")

st.text("Для отображение подсчёта должен быть создан запрос на подсчёт.")

import requests
import streamlit as st

# Fetch the list of counting requests
response = requests.get('http://backend:8543/count/')
if response.status_code == 200:
    counting_requests = response.json()
else:
    st.error('Не получается получить список запросов. Проверьте доступ к серверу.')

# Create a list of pairs (camera, product)
pairs = [(request['camera_name'], request['product_name']) for request in counting_requests]

# Let the user select a pair
selected_pair = st.selectbox('Выберите пару (камера, продукт)', pairs)

# Find the selected counting request
selected_request = next((request for request in counting_requests if request['camera_name'] == selected_pair[0] and request['product_name'] == selected_pair[1]), None)

if selected_request is not None:
    # Get the RTSP and product name from the selected counting request
    rtsp = selected_request['rtsp_stream']
    product_name = selected_request['product_name']
    selection_area = selected_request['selection_area']
    counting_line = selected_request['counting_line']
    model = YOLO('/model/yolo.pt')

    helper.play_rtsp_stream(model, rtsp, counting_line, selection_area)

else:
    st.error('Не удалось найти выбранную пару. Проверьте данные.')
