import os
from datetime import datetime
from ultralytics import YOLO
import requests
import pickle
import supervision as sv

def process_data(frame, tracker, line_counter):
    # for image in images:
    model = YOLO('/model/yolo.pt')
    image = pickle.loads(frame)
    tracker = pickle.loads(tracker)
    line_counter = pickle.loads(line_counter)
    results = model(image)[0]
    detections = sv.Detections.from_ultralytics(results)
    detections = tracker.update_with_detections(detections)
    line_counter.trigger(detections=detections)

    return tracker, line_counter.out_count

