import os
from datetime import datetime
from ultralytics import YOLO
from celery import Celery
import requests
import pickle
import supervision as sv

celery = Celery(__name__)
celery.conf.broker_url = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379")
celery.conf.result_backend = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379")


@celery.task(name="process_data", queue="queue2")
def process_data(frame_pickled, tracker, line_counter, camera_id, product_id):
    # for image in images:
    model = YOLO('/model/yolo.pt')
    image = pickle.loads(frame_pickled)
    tracker = pickle.loads(tracker)
    line_counter = pickle.loads(line_counter)
    results = model(image)[0]
    detections = sv.Detections.from_ultralytics(results)
    detections = tracker.update_with_detections(detections)
    line_counter.trigger(detections=detections)

    # Return a dictionary containing the resulting variables
    return {
        "images": image,
        "count": line_counter.out_count,
        "tracker": tracker,
        "line_counter": line_counter,
        "camera_id": camera_id,
        "product_id": product_id
    }


@celery.task(name="send_count", queue="queue2")
def send_count(result_dict):
    # Post the resulting values to the FastAPI endpoint
    response = requests.post(
        "http://localhost:8000/counting_result/",  # Replace with your FastAPI server URL
        json={
            "camera_id": result_dict["camera_id"],
            "product_id": result_dict["product_id"],
            "start_period": str(datetime.now()),  # Replace with the actual start time
            "end_period": str(datetime.now()),  # Replace with the actual end time
            "count": result_dict["count"]
        }
    )

    # Check the response
    if response.status_code != 200:
        print(f"Failed to post data to /counting_result/: {response.text}")

    return result_dict @ celery.task(name="process", queue="queue2")
