# producer.py
import pickle

import cv2
from multiprocessing import Process, Queue

from ultralytics import YOLO

from .worker import process_data
import supervision as sv
class Producer:
    def __init__(self, video_sources):
        self.video_sources = video_sources

    def start(self):
        processes = []
        # create instance of BoxAnnotator and LineCounterAnnotator
        LINE_START = sv.Point(0, 2000)
        LINE_END = sv.Point(3000, 2000)
        for i, video_source in enumerate(self.video_sources):
            line_counter = sv.LineZone(start=LINE_START, end=LINE_END)
            tracker = sv.ByteTrack()
            process = Process(target=self._read_video, args=(video_source,
                                                             tracker, line_counter))
            processes.append(process)
            process.start()

        for process in processes:
            process.join()

    def _read_video(self, video_source, tracker, line_counter):
            cap = cv2.VideoCapture(video_source)
            while True:
                ret, frame = cap.read()
                frame_pickled = pickle.dumps(frame)
                tracker = pickle.dumps(tracker)
                line_counter = pickle.dumps(line_counter)
                if not ret:
                    break
                process_data.delay(frame_pickled, tracker, line_counter, 1, 1)  # Отправляем кадр на обработку в Celery
            cap.release()
