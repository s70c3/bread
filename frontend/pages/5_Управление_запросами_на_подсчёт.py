import streamlit as st
from streamlit_drawable_canvas import st_canvas
import cv2
from PIL import Image
import requests


from pages.utils.password import check_password

if not check_password():
    st.stop()  # Do not continue if check_password is not True.


st.header("Добавление камер")


# Main page heading
st.subheader("Активные камеры")

# Make a GET request to the /count/ endpoint
response = requests.get("http://backend:8543/count/")

# Check if the request was successful
if response.status_code == 200:
    # Get the counting requests from the response
    counting_requests = response.json()

    # Display the counting requests in a table
    st.table(counting_requests)

    # Allow the user to select a counting request to update or delete
    request_id = st.selectbox('Выберите камеру для управления', [req['name'] for req in counting_requests])

    # Ask the user if they want to edit or delete the selected row
    action = st.selectbox('Вы хотите изменить или удалить камеру?', options=['Изменить', 'Удалить'])
    request = next((req for req in counting_requests if
                    (req['name'] == request_id)), None)

    if action == 'Изменить':
        with st.form(key='edit_form'):
        # If the user chooses to update a camera
        # Display a form with the current details of the camera
            if request:
                    new_name = st.text_input("Название камеры", request['name'])
                    new_address = st.text_input("rtsp-адрес камеры",  request['rtsp_stream'])
                    new_description = st.text_input("Описание камеры", request['description'])
                    new_selection_area = st.text_input('Зона выбора', request['selection_area'])
                    if len(new_selection_area)==0:
                        new_selection_area = None
                    new_counting_line = st.text_input('Линия подсчёта', request['counting_line'])
                    if len(new_counting_line)==0:
                        new_counting_line = None
                    new_status = st.radio('Статус:', [0, 1], format_func=lambda x: 'Работает' if x == 1 else 'Выключена')
                    submit_button = st.form_submit_button(label='Подтвердить')

                    if submit_button:
                    # Send the updated counting request to the backend
                        response = requests.put(f"http://backend:8543/count/{request['request_id']}", json={
                            'request_id': request_id,
                            "name": new_name,
                            "rtsp_stream": new_address,
                            "description": new_description,
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
            response = requests.delete(f"http://backend:8543/count/{request['request_id']}")
            if response.status_code == 200:
                st.success("Запрос на подсчёт успешно удалён.")
            else:
                st.error('Не удалось удалить запрос.')
else:
    st.error("Не удалось получить текущие подключения.")

# Main page heading
st.subheader("Создание новой камеры и выбор зон подсчёта.")

name = st.text_input("Введите название камеры")

description = st.text_input("Введите описание камеры")

stream_address = st.text_input("Введите rtsp-адрес камеры")

if len(stream_address)>0:
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

        #Coordinates by default
        x1, x2, y1, y2 = 0, frame.shape[0], 0, frame.shape[1]
        lx1, ly1, lx2, ly2 =0,  frame.shape[1]-50, frame.shape[0], frame.shape[1]-50
        # The data in the canvas (lines, shapes, etc) is in the `canvas_result.json_data` attribute
        #Bounding box
        if canvas_result_square.json_data is not None and len(canvas_result_square.json_data["objects"])>0:
            # Extract the coordinates of the square
            x1 = canvas_result_square.json_data["objects"][0]["left"]
            x2 = x1 + canvas_result_square.json_data["objects"][0]["width"]
            y1 = canvas_result_square.json_data["objects"][0]["top"]
            y2 = y1 + canvas_result_square.json_data["objects"][0]["height"]
            st.write("Координаты ограничивающей области:", x1, y1, x2, y2)
        #Counter line
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
                "name": name,
                "rtsp_stream": stream_address,
                "description": description,
                'selection_area': str([x1, y1, x2, y2]),
                'counting_line': str([lx1, ly1, lx2, ly2]),
                'status': 1
            })
            if response.status_code == 200:
                st.write('Запрос на подсчёт отправлен успешно.')
            else:
                st.error('Не удалось отправить данные.')
                st.write(response.text)
    except cv2.error:
        if st.button('Подтвердить'):
            response = requests.post('http://backend:8543/count/', json={
                "name": name,
                "rtsp_stream": stream_address,
                "description": description,
                'selection_area': None,
                'counting_line': None,
                'status': 0
            })
            if response.status_code == 200:
                st.write('Запрос на подсчёт отправлен успешно, но без указания областей подсчёта.')
            else:
                st.write('Не удалось отправить данные.')
        st.error("Нет подключения к потоку. Запрос можно отправить без указания области.")
