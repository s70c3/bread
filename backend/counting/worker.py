import os
from datetime import datetime
from ultralytics import YOLO
import requests
import pickle
import supervision as sv

def process_data(frame, tracker, line_counter, camera_id, product_id):
    # for image in images:
    model = YOLO('/model/yolo.pt')
    results = model(frame)[0]
    detections = sv.Detections.from_ultralytics(results)
    print("ids", product_id, detections.class_id[0])
    detections = detections[detections.class_id == product_id]
    detections = tracker.update_with_detections(detections)
    line_counter.trigger(detections=detections)

    return tracker, line_counter.out_count

