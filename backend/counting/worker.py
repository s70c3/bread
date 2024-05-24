
from ultralytics import YOLO
import supervision as sv

def process_data(frame, tracker, line_counter, camera_id, product_name):
    # for image in images:
    model = YOLO('/model/yolo.pt')
    results = model(frame)[0]
    detections = sv.Detections.from_ultralytics(results)
    print("ids", product_name, detections['class_name'][0])
    detections = detections[detections['class_name'] == product_name]
    detections = tracker.update_with_detections(detections)
    line_counter.trigger(detections=detections)

    return tracker, line_counter.out_count

