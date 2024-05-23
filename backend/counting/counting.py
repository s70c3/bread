# producer.py
import ast
import pickle
import time

import cv2
from multiprocessing import Process, Queue
import requests
from ultralytics import YOLO

from .worker import process_data
import supervision as sv
class Producer:
    _instance = None
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Producer, cls).__new__(cls)
        return cls._instance
    def __init__(self, video_sources=None):
        if video_sources is None:
            video_sources = []
        self.video_sources = video_sources
        self.processes = []
        self.is_running = False

    def start(self):
        if self.is_running:
            return "Processes are already running"

        for i, video_source in enumerate(self.video_sources):
            rtsp, camera_id, bread_id, selection_area, counting_line = video_source
            counting_line = ast.literal_eval(counting_line)
            LINE_START = sv.Point(counting_line[0], counting_line[1])
            LINE_END = sv.Point(counting_line[2], counting_line[3])

            line_counter = sv.LineZone(start=LINE_START, end=LINE_END)
            tracker = sv.ByteTrack()
            process = Process(target=self._read_video, args=(rtsp,
                                                             tracker, line_counter))
            self.processes.append(process)
            process.start()

        for process in self.processes:
            process.join()

        print("Количество процессов: ",len(self.processes))
        self.is_running = True

    def add_stream(self, video_source, ):
        # create instance of BoxAnnotator and LineCounterAnnotator
        rtsp, camera_id, bread_id, selection_area, counting_line = video_source
        counting_line = ast.literal_eval(counting_line)
        LINE_START = sv.Point(counting_line[0], counting_line[1])
        LINE_END = sv.Point(counting_line[2], counting_line[3])

        self.video_sources.append(video_source)
        line_counter = sv.LineZone(start=LINE_START, end=LINE_END)
        tracker = sv.ByteTrack()
        process = Process(target=self._read_video, args=(video_source,
                                                         tracker, line_counter, camera_id, bread_id))
        self.processes.append(process)
        process.start()

        process.join()

    def _read_video(self, video_source, tracker, line_counter, camera_id=1, product_id=1):
            cap = cv2.VideoCapture(video_source)
            frame_counter = 0
            while True:
                ret, frame = cap.read()
                frame_counter+=1
                if not ret:
                    break
                tracker, count = process_data(frame, tracker, line_counter, camera_id, product_id)
                if frame_counter % 20 == 0:

                    data = {
                        "camera_id": camera_id,
                        "product_id": product_id,
                        "count": count,
                        "timestamp" : time.time()
                    }
                    response = requests.post("http://localhost:8000/counting_result/", json=data)
                    if response.status_code == 200:
                        print("Data sent successfully")
                    else:
                        print("Failed to send data")

            cap.release()

    def stop(self):
        if not self.is_running:
            return "No processes to stop"

        for process in self.processes:
            process.terminate()
        self.processes = []

        self.is_running = False
