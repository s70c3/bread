
from ultralytics import YOLO
import supervision as sv
import cv2
import numpy as np
def process_data(frame, model, tracker, line_counter,selection_area, current_class, zero_frames):
    frame = cv2.resize(frame, (720, int(720 * (9 / 16))))
    frame = frame[selection_area[1]:selection_area[3], selection_area[0]:selection_area[2]]
    results = model(frame)[0]
    detections = sv.Detections.from_ultralytics(results)
    need_to_store = None
    total_objects = len(detections)
    if total_objects == 0:
        zero_frames += 1
        if zero_frames >= 20:
            current_class = "empty"
    else:
        zero_frames = 0
        classes, counts = np.unique(detections['class_name'], return_counts=True)
        for cl, c in zip(classes, counts):
            if c / total_objects > 0.9:
                if cl != current_class:
                    need_to_store = current_class, line_counter.out_count
                    current_class = cl
                    line_counter.out_count = 0
    detections = detections[detections['class_name'] == current_class]
    detections = tracker.update_with_detections(detections)
    line_counter.trigger(detections=detections)

    return tracker, line_counter, current_class, zero_frames, need_to_store

