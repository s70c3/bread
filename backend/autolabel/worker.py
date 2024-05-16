import os

from celery import Celery
from .autolabel import *

celery = Celery(__name__)
celery.conf.broker_url = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379")
celery.conf.result_backend = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379")


@celery.task(name="label")
def label_data(video_stream, conveyor, dist, name):
    source = create_images(video_stream, conveyor, dist)
    dataset = label(source, dist)
    train_yolo(dataset, name)

    # time.sleep(int(task_type) * 10)
    return True
