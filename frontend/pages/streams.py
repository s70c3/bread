# Python In-built packages
from pathlib import Path
import PIL

# External packages
import streamlit as st

# Local Modules
import pages.utils.helper as helper
import pages.utils.settings as settings

# Setting page layout
st.set_page_config(
    page_title="Object Detection using YOLOv8",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Main page heading
st.title("Подсчёт объектов в реальном времени")

# Sidebar
st.sidebar.header("Подсчёт в режиме онлайн")

confidence = float(st.sidebar.slider(
    "Select Model Confidence", 25, 100, 40)) / 100

model_path = Path(settings.DETECTION_MODEL)

# Load Pre-trained ML Model
try:
    model = helper.load_model(model_path)
except Exception as ex:
    st.error(f"Unable to load model. Check the specified path: {model_path}")
    st.error(ex)

st.sidebar.header("Image/Video Config")

import requests

response = requests.get('http://backend:8000/camera')

if response.status_code == 200:
    sources = response.json()
    sources = {camera['name']: camera['rtsp_stream'] for camera in sources['cameras']}
    print(sources)
else:
    print('Failed to get sources')

source_radio = st.sidebar.radio(
    "Выберите камеру", sources.keys())

stream_address= str(sources.get(source_radio))

helper.play_rtsp_stream(confidence, model, stream_address)
