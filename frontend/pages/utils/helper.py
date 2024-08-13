import ast

from ultralytics import YOLO
import streamlit as st
import cv2
import supervision as sv
import numpy as np


def load_model(model_path):
    """
    Loads a YOLO object detection model from the specified model_path.

    Parameters:
        model_path (str): The path to the YOLO model file.

    Returns:
        A YOLO object detection model.
    """
    model = YOLO(model_path)
    return model


def _display_detected_frames(model, st_frame, st_text, frame, tracker=None, line_counter=None,
                             line_annotator=None, box_annotator=None, selection_area=None,
                             current_class=None, zero_frames=0, mapping=None):
    """
    Display the detected objects on a video frame using the YOLOv8 model.

    Args:
    - conf (float): Confidence threshold for object detection.
    - model (YoloV8): A YOLOv8 object detection model.
    - st_frame (Streamlit object): A Streamlit object to display the detected video.
    - image (numpy array): A numpy array representing the video frame.
    - is_display_tracking (bool): A flag indicating whether to display object tracking (default=None).

    Returns:
    None
    """

    # Resize the image to a standard size
    frame = cv2.resize(frame, (720, int(720 * (9 / 16))))
    frame = frame[selection_area[1]:selection_area[3], selection_area[0]:selection_area[2]]
    results = model(frame)[0]

    detections = sv.Detections.from_ultralytics(results)
    total_objects = len(detections)
    if len(detections) == 0:
        zero_frames += 1
        if zero_frames >= 20:
            current_class = "empty"
    else:
        zero_frames = 0
        classes, counts = np.unique(detections['class_name'], return_counts=True)
        for cl, c in zip(classes, counts):
            if c / total_objects > 0.9:
                if cl != current_class:
                    current_class = cl
                    line_counter.out_count = 0
    detections = detections[detections['class_name'] == current_class]
    detections = tracker.update_with_detections(detections)

    # updating line counter
    line_counter.trigger(detections=detections)
    # format custom labels
    # dict maping class_id to class_name

    # frame = box_annotator.annotate(scene=frame, detections=detections)
    line_annotator.annotate(frame=frame, line_counter=line_counter)
    box_annotator.annotate(scene=frame, detections=detections)

    label_annotator = sv.LabelAnnotator()
    # labels = [
    #     f"{tracker_id} {mapping[class_name]}"
    #     for class_name, tracker_id
    #     in zip(detections['class_name'], detections.tracker_id)
    # ]
    # frame = label_annotator.annotate(
    #     scene=frame, detections=detections)  #, labels=labels)

    # # Plot the detected objects on the video frame
    st_frame.image(frame,
                   caption='Detected Video',
                   channels="BGR",
                   use_column_width=True
                   )

    st_text.markdown(f'''**Сейчас на конвейере:** {current_class},  количество с начала:{line_counter.out_count}''')
    return tracker, line_counter, zero_frames, current_class


def play_rtsp_stream(model, source_rtsp, counting_line, selection_area, mapping):
    """
    Plays an rtsp stream. Detects Objects in real-time using the YOLOv8 object detection model.

    Parameters:
        conf: Confidence of YOLOv8 model.
        model: An instance of the `YOLOv8` class containing the YOLOv8 model.

    Returns:
        None

    Raises:
        None
    """
    tracker = sv.ByteTrack()
    if counting_line is None:
        counting_line = [0, 500, 3000, 500]
    else:
        counting_line = ast.literal_eval(counting_line)
    if selection_area is None:
        selection_area = [0, 0, -1, -1]
    else:
        selection_area = ast.literal_eval(selection_area)
    LINE_START = sv.Point(counting_line[0] - selection_area[0], counting_line[1] - selection_area[1])
    LINE_END = sv.Point(counting_line[2] - selection_area[0], counting_line[3] - selection_area[1])
    box_annotator = sv.BoundingBoxAnnotator(color=sv.ColorPalette.default(), thickness=1)
    line_counter = sv.LineZone(start=LINE_START, end=LINE_END)
    # create instance of BoxAnnotator and LineCounterAnnotator
    line_annotator = sv.LineZoneAnnotator(thickness=1, text_thickness=1, text_scale=0.3)
    zero_frames = 0
    current_class = "empty"
    try:
        vid_cap = cv2.VideoCapture(source_rtsp)
        st_frame = st.empty()
        st_text = st.empty()
        if vid_cap.isOpened() is False:
            st.error("Нет соединения с потоком")
        while (vid_cap.isOpened()):
            success, image = vid_cap.read()

            if success:
                tracker, line_counter, zero_frames, current_class = _display_detected_frames(
                    model,
                    st_frame,
                    st_text,
                    image,
                    tracker,
                    line_counter,
                    line_annotator,
                    box_annotator, selection_area,
                    current_class,
                    zero_frames,
                    mapping

                )
            else:
                vid_cap.release()
                break
    except Exception as e:
        vid_cap.release()
        st.error("Не получен видео поток: " + str(e))
