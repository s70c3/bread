
from ultralytics import YOLO
import streamlit as st
import cv2
#
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


def display_tracker_options():
    display_tracker = st.radio("Display Tracker", ('Yes', 'No'))
    is_display_tracker = True if display_tracker == 'Yes' else False
    if is_display_tracker:
        tracker_type = st.radio("Tracker", ("bytetrack.yaml", "botsort.yaml"))
        return is_display_tracker, tracker_type
    return is_display_tracker, None


def _display_detected_frames(conf, model, st_frame, image, is_display_tracking=None, tracker=None):
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
    image = cv2.resize(image, (720, int(720*(9/16))))

    # Display object tracking, if specified
    if is_display_tracking:
        res = model.track(image, conf=conf, persist=True, tracker=tracker)
    else:
        # Predict the objects in the image using the YOLOv8 model
        res = model.predict(image, conf=conf)

    # # Plot the detected objects on the video frame
    res_plotted = res[0].plot()
    st_frame.image(res_plotted,
                   caption='Detected Video',
                   channels="BGR",
                   use_column_width=True
                   )



def play_rtsp_stream(conf, model):
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
    source_rtsp = st.sidebar.text_input("rtsp stream url:")
    st.sidebar.caption('Example URL: rtsp://admin:12345@192.168.1.210:554/Streaming/Channels/101')
    tracker = sv.ByteTrack()
    if st.sidebar.button('Detect Objects'):
        try:
            vid_cap = cv2.VideoCapture(source_rtsp)
            st_frame = st.empty()
            while (vid_cap.isOpened()):
                success, image = vid_cap.read()
                if success:
                    _display_detected_frames(conf,
                                             model,
                                             st_frame,
                                             image,
                                             is_display_tracker,
                                             tracker
                                             )
                else:
                    vid_cap.release()
                    # vid_cap = cv2.VideoCapture(source_rtsp)
                    # time.sleep(0.1)
                    # continue
                    break
        except Exception as e:
            vid_cap.release()
            st.sidebar.error("Error loading RTSP stream: " + str(e))



# model = YOLO(model_path)
# # Resize the image to a standard size
# # image = cv2.resize(image, (720, int(720*(9/16))))
#
# # Display object tracking, if specified
#
# # Track objects in frames if available
# results = model(frame)[0]
# # frame = counter.start_counting(frame, results)
# detections = sv.Detections.from_ultralytics(results)
# detections = tracker.update_with_detections(detections)
# LINE_START = sv.Point(0, 2000)
# LINE_END = sv.Point(3000, 2000)
#
# line_counter = sv.LineZone(start=LINE_START, end=LINE_END)
# # create instance of BoxAnnotator and LineCounterAnnotator
# line_annotator = sv.LineZoneAnnotator(thickness=4, text_thickness=4, text_scale=2)
# box_annotator = sv.BoxAnnotator(color=sv.ColorPalette.default(), thickness=4, text_thickness=4, text_scale=2)
#
# # updating line counter
# line_counter.trigger(detections=detections)
# # format custom labels
# # dict maping class_id to class_name
#
# frame = box_annotator.annotate(scene=frame, detections=detections)
# line_annotator.annotate(frame=frame, line_counter=line_counter)
#
# # {"Хлеба": "rtsp://admin:Novichek2024$$@localhost:8080/ISAPI/Streaming/Channels/101"})