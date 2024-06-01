# Python In-built packages

# External packages
import streamlit as st

# Local Modules
import pages.utils.helper as helper
from ultralytics import YOLO

from pages.utils.password import check_password

if not check_password():
    st.stop()  # Do not continue if check_password is not True.


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
response = requests.get('http://bread-backend:8543/count/')
if response.status_code == 200:
    counting_requests = response.json()
else:
    st.error('Не получается получить список запросов. Проверьте доступ к серверу.')
try:
    response = requests.get('http://bread-backend:8543/bread/')
    breads = response.json()['breads']
    mapping = dict()
    for product in breads:
        mapping[product['name']] = product['id']
except Exception as e:
    mapping = None
    st.error("Невозможно получить список продуктов. Записи могут отображаться некорректно.")

# Create a list of pairs (camera, product)
pairs = [request['camera_name'] for request in counting_requests]

# Let the user select a pair
selected_pair = st.selectbox('Выберите камеру для создания подсчёта.', pairs)

# Find the selected counting request
selected_request = next((request for request in counting_requests if request['camera_name'] == selected_pair[0]), None)

if selected_request is not None:
    # Get the RTSP and product name from the selected counting request
    rtsp = selected_request['rtsp_stream']
    selection_area = selected_request['selection_area']
    counting_line = selected_request['counting_line']
    model = YOLO('/model/yolo.pt')

    helper.play_rtsp_stream(model, rtsp, counting_line, selection_area, mapping)

else:
    st.error('Не удалось найти выбранную пару. Проверьте данные.')
