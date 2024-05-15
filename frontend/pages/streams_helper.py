
from ultralytics import YOLO
import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase
import numpy as np
from PIL import Image
import av
import cv2
import supervision as sv

model = YOLO(model_path)
# Resize the image to a standard size
# image = cv2.resize(image, (720, int(720*(9/16))))

# Display object tracking, if specified
tracker = sv.ByteTrack()
# Track objects in frames if available
results = model(frame)[0]
# frame = counter.start_counting(frame, results)
detections = sv.Detections.from_ultralytics(results)
detections = tracker.update_with_detections(detections)
LINE_START = sv.Point(0, 2000)
LINE_END = sv.Point(3000, 2000)

line_counter = sv.LineZone(start=LINE_START, end=LINE_END)
# create instance of BoxAnnotator and LineCounterAnnotator
line_annotator = sv.LineZoneAnnotator(thickness=4, text_thickness=4, text_scale=2)
box_annotator = sv.BoxAnnotator(color=sv.ColorPalette.default(), thickness=4, text_thickness=4, text_scale=2)

# updating line counter
line_counter.trigger(detections=detections)
# format custom labels
# dict maping class_id to class_name

frame = box_annotator.annotate(scene=frame, detections=detections)
line_annotator.annotate(frame=frame, line_counter=line_counter)

# {"Хлеба": "rtsp://admin:Novichek2024$$@localhost:8080/ISAPI/Streaming/Channels/101"})