
from ultralytics import YOLO
import supervision as sv
import cv2
def process_data(frame, tracker, line_counter, camera_id, product_name):
    # for image in images:
    frame = cv2.resize(frame, (720, int(720 * (9 / 16))))
    model = YOLO('/model/yolo.pt')
    results = model(frame)[0]
    detections = sv.Detections.from_ultralytics(results)
    detections = detections[detections['class_name'] == product_name]
    detections = tracker.update_with_detections(detections)
    line_counter.trigger(detections=detections)

    return tracker, line_counter.out_count

