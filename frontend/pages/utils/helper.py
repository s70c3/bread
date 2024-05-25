import ast

from ultralytics import YOLO
import streamlit as st
import cv2
import supervision as sv
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


def _display_detected_frames( model, st_frame, frame,  tracker=None, line_counter=None, line_annotator=None, box_annotator=None):
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
    results = model(frame)[0]

    detections = sv.Detections.from_ultralytics(results)
    detections = tracker.update_with_detections(detections)

    # updating line counter
    line_counter.trigger(detections=detections)
    # format custom labels
    # dict maping class_id to class_name

    # frame = box_annotator.annotate(scene=frame, detections=detections)
    line_annotator.annotate(frame=frame, line_counter=line_counter)

    label_annotator = sv.LabelAnnotator()
    labels = [
        f"{class_name} {confidence:.2f}"
        for class_name, confidence
        in zip(detections['class_name'], detections.confidence)
    ]
    frame = label_annotator.annotate(
        scene=frame, detections=detections, labels=labels)


    # # Plot the detected objects on the video frame
    st_frame.image(frame,
                   caption='Detected Video',
                   channels="BGR",
                   use_column_width=True
                   )

    return tracker, line_counter



def play_rtsp_stream(model, source_rtsp, counting_line):
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
    counting_line = ast.literal_eval(counting_line)
    LINE_START = sv.Point(counting_line[0], counting_line[1])
    LINE_END = sv.Point(counting_line[2], counting_line[3])

    box_annotator = sv.BoxAnnotator(color=sv.ColorPalette.default(), thickness=1, text_thickness=1, text_scale=1)
    line_counter = sv.LineZone(start=LINE_START, end=LINE_END)
    # create instance of BoxAnnotator and LineCounterAnnotator
    line_annotator = sv.LineZoneAnnotator(thickness=1, text_thickness=1, text_scale=1)
    try:
        vid_cap = cv2.VideoCapture(source_rtsp)
        st_frame = st.empty()
        if vid_cap.isOpened() is False:
            st.error("Нет соединения с потоком")
        while (vid_cap.isOpened()):
            success, image = vid_cap.read()

            if success:
                tracker, line_counter = _display_detected_frames(
                                         model,
                                         st_frame,
                                         image,
                                         tracker,
                                         line_counter,
                                         line_annotator,
                                         box_annotator
                                         )
            else:
                vid_cap.release()
                break
    except Exception as e:
        vid_cap.release()
        st.error("Не получен видео поток: " + str(e))
