import streamlit as st
from streamlit_drawable_canvas import st_canvas
import cv2
from PIL import Image
import requests

# Fetch the list of cameras
response = requests.get('http://backend:8000/camera')
if response.status_code == 200:
    sources = response.json()
    sources = {camera['name']: camera['rtsp_stream'] for camera in sources['cameras']}
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
source_radio = st.sidebar.radio("Выберите камеру", sources.keys())
bread_select = st.sidebar.selectbox('Выберите хлебобулочное изделие', list(breads.keys()))

stream_address= str(sources.get(source_radio))

# Fetch the RTSP stream
stream = cv2.VideoCapture(stream_address)

# Capture a frame from the stream
ret, frame = stream.read()

# Convert the frame to RGB
frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
frame = cv2.resize(frame, (720, int(720*(9/16))))


# Create a drawable canvas with the frame as the background for drawing the square
st.markdown("## Выделите область, окружающую конвейер.")
canvas_result_square = st_canvas(
    fill_color="rgba(255, 165, 0, 0.3)",  # Fixed fill color with some opacity
    stroke_width=2,
    stroke_color='#e00',
    background_image=Image.fromarray(frame),
    update_streamlit=True,
    height=frame.shape[0],
    width=frame.shape[1],
    drawing_mode='rect',
    key="canvas_square",
)

# Create a drawable canvas with the frame as the background for drawing the line
st.markdown("## Draw a line")
canvas_result_line = st_canvas(
    fill_color="rgba(255, 165, 0, 0.3)",  # Fixed fill color with some opacity
    stroke_width=2,
    stroke_color='#e00',
    background_image=Image.fromarray(frame),
    update_streamlit=True,
    height=frame.shape[0],
    width=frame.shape[1],
    drawing_mode='line',
    key="canvas_line",
)

# The data in the canvas (lines, shapes, etc) is in the `canvas_result.json_data` attribute
if canvas_result_square.json_data is not None and len(canvas_result_square.json_data["objects"])>0:
    # Extract the coordinates of the square
    x1 = canvas_result_square.json_data["objects"][0]["left"]
    x2 = x1 + canvas_result_square.json_data["objects"][0]["width"]
    y1 = canvas_result_square.json_data["objects"][0]["top"]
    y2 = y1 + canvas_result_square.json_data["objects"][0]["height"]
    st.write("Square data:", x1, y1, x2, y2)

if canvas_result_line.json_data is not None and len(canvas_result_line.json_data["objects"])>0:
    # Extract the coordinates of the line
    lx1 = canvas_result_line.json_data["objects"][0]["left"]
    lx2 = lx1 + canvas_result_line.json_data["objects"][0]["width"]
    ly1 = canvas_result_line.json_data["objects"][0]["top"]
    ly2 = ly1 + canvas_result_line.json_data["objects"][0]["height"]
    st.write("Line data:", lx1, ly1, lx2, ly2)

# Send the data to the backend
if st.button('Submit'):
    response = requests.post('http://backend:8000/label/', json={
        'square': [x1, y1, x2, y2],
        'line': [lx1, ly1, lx2, ly2],
        'camera_id': sources[source_radio],
        'bread_product_id': breads[bread_select]
    })
    if response.status_code == 200:
        st.write('Data sent successfully')
    else:
        st.write('Failed to send data')
        st.write(response.text)