import streamlit as st
from streamlit_drawable_canvas import st_canvas
import cv2
from PIL import Image
import requests

st.header("Запрос на подсчёт хлебобулочных изделий")


# Main page heading
st.subheader("Активные запросы на подсчёт")

# Make a GET request to the /count/ endpoint
response = requests.get("http://backend:8543/count/")

# Check if the request was successful
if response.status_code == 200:
    # Get the counting requests from the response
    counting_requests = response.json()

    # Display the counting requests in a table
    st.table(counting_requests)

    # Allow the user to select a counting request to update or delete
    request_id = st.selectbox('Выберите запрос для управления', [(req['camera_name'], req['product_name']) for req in counting_requests])

    # Ask the user if they want to edit or delete the selected row
    action = st.selectbox('Вы хотите изменить или удалить запрос?', options=['Изменить', 'Удалить'])
    request = next((req for req in counting_requests if
                    (req['camera_name'] == request_id[0] and req['product_name'] == request_id[1])), None)

    if action == 'Изменить':
        with st.form(key='edit_form'):
        # If the user chooses to update a counting request
            # Display a form with the current details of the counting request
           # st.text(request)
            if request:
                    new_selection_area = st.text_input('Зона выбора', request['selection_area'])
                    new_counting_line = st.text_input('Линия подсчёта', request['counting_line'])
                    new_status = st.radio('Статус:', [0, 1], format_func=lambda x: 'Работает' if x == 1 else 'Выключена')
                    submit_button = st.form_submit_button(label='Подтвердить')

                    if submit_button:
                    # Send the updated counting request to the backend
                        response = requests.put(f"http://backend:8543/count/{request['id']}", json={
                            'camera_id': request['camera_id'],
                            'product_id' : request['product_id'],
                            'selection_area': new_selection_area,
                            'counting_line': new_counting_line,
                            'status' : int(new_status)
                        })
                        if response.status_code == 200:
                            st.success('Запрос на подсчёт успешно обновлен.')
                        else:
                            st.error('Не удалось обновить подсчёт.')

    # If the user chooses to delete a counting request
    if action =='Удалить':
        # Confirm the deletion before sending the delete request to the backend
        if st.button('Подтвердить удаление'):
            response = requests.delete(f"http://backend:8543/count/{request['id']}")
            if response.status_code == 200:
                st.success("Запрос на подсчёт успешно удалён.")
            else:
                st.error('Не удалось удалить запрос.')


else:
    st.error("Не удалось получить текущие подключения.")

# Main page heading
st.subheader("Создание запроса на подсчёт")

st.text("Для запроса необходимо выбрать соответствующие камеру и изделие.")
st.text("Добавьте камеру в на странице 'Управление камерами', а продукт на странице 'Управление продуктами'.")
# Fetch the list of cameras
response = requests.get('http://backend:8543/camera')
if response.status_code == 200:
    sources_raw = response.json()
    sources = {camera['name']: camera['rtsp_stream'] for camera in sources_raw['cameras']}
    camera_ids = {camera['name']: camera['camera_id'] for camera in sources_raw['cameras']}
else:
    print('Не получается получить список камер. Проверьте доступ к серверу.')

# Fetch the list of bread products
response = requests.get('http://backend:8543/bread/')
if response.status_code == 200:
    breads = response.json()
    breads = {bread['name']: bread['product_id'] for bread in breads['breads']}
else:
    print('Не получается получить список хлебобулочных изделий. Проверьте доступ к серверу.')

# Let the user select a camera and a bread product
source_radio = st.radio("Выберите камеру", sources.keys())
bread_select = st.selectbox('Выберите хлебобулочное изделие', list(breads.keys()))

stream_address= str(sources.get(source_radio))
try:
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
    st.markdown("## Нарисуйте линию подсчёта")
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

    x1, x2, y1, y2 = 0, frame.shape[0], 0, frame.shape[1]
    lx1, ly1, lx2, ly2 =0,  frame.shape[1]-50, frame.shape[0], frame.shape[1]-50
    # The data in the canvas (lines, shapes, etc) is in the `canvas_result.json_data` attribute
    if canvas_result_square.json_data is not None and len(canvas_result_square.json_data["objects"])>0:
        # Extract the coordinates of the square
        x1 = canvas_result_square.json_data["objects"][0]["left"]
        x2 = x1 + canvas_result_square.json_data["objects"][0]["width"]
        y1 = canvas_result_square.json_data["objects"][0]["top"]
        y2 = y1 + canvas_result_square.json_data["objects"][0]["height"]
        st.write("Координаты ограничивающей области:", x1, y1, x2, y2)

    if canvas_result_line.json_data is not None and len(canvas_result_line.json_data["objects"])>0:
        # Extract the coordinates of the line
        lx1 = canvas_result_line.json_data["objects"][0]["left"] - canvas_result_line.json_data["objects"][0]["width"]//2
        lx2 = lx1 + canvas_result_line.json_data["objects"][0]["width"]
        ly1 = canvas_result_line.json_data["objects"][0]["top"]
        ly2 = ly1 + canvas_result_line.json_data["objects"][0]["height"]
        st.write("Координаты линии подсчёта:", lx1, ly1, lx2, ly2)

    # Send the data to the backend
    if st.button('Подтвердить'):
        response = requests.post('http://backend:8543/count/', json={
            'selection_area': str([x1, y1, x2, y2]),
            'counting_line': str([lx1, ly1, lx2, ly2]),
            'camera_id': camera_ids[source_radio],
            'product_id': breads[bread_select],
            'status' : 1
        })
        if response.status_code == 200:
            st.write('Запрос на подсчёт отправлен успешно.')
        else:
            st.write('Не удалось отправить данные.')

            st.write(response.text)
except cv2.error:
    if st.button('Подтвердить'):
        response = requests.post('http://backend:8543/count/', json={
            'selection_area': str([0, 0, 3000, 3000]),
            'counting_line': str([0, 300, 3000, 300]),
            'camera_id': camera_ids[source_radio],
            'product_id': breads[bread_select],
            'status' : 0
        })
        if response.status_code == 200:
            st.write('Запрос на подсчёт отправлен успешно.')
        else:
            st.write('Не удалось отправить данные.')
    st.error("Нет подключения к потоку. Запрос можно отправить без указания области.")
