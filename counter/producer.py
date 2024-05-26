# producer_old.py
import ast
import pickle
import time

import cv2

import multiprocessing as mp
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
    def __init__(self, video_source=None):
        if video_source is None:
            video_source = ()
        self.video_source = video_source
        self.is_running = False

    def start(self):
        if self.is_running:
            return "Процесс уже запущен."

        self.add_stream(*self.video_source)
        print("Количество процессов: ",len(self.video_source))
        self.is_running = True

    def add_stream(self, rtsp, camera_id, bread_id, name, selection_area, counting_line, status ):
        # create instance of BoxAnnotator and LineCounterAnnotator

        counting_line = ast.literal_eval(counting_line)
        selection_area = ast.literal_eval(selection_area)
        LINE_START = sv.Point(counting_line[0] - selection_area[1], counting_line[1])
        LINE_END = sv.Point(counting_line[2] - selection_area[1], counting_line[3])
        if status == 0:
            return
        line_counter = sv.LineZone(start=LINE_START, end=LINE_END)
        tracker = sv.ByteTrack()
        self._read_video(rtsp, tracker, line_counter, camera_id, bread_id, name, selection_area)

    def _read_video(self, rtsp, tracker, line_counter, camera_id=1, product_id=1, name="notaclassname", selection_area=None):
            cap = cv2.VideoCapture(rtsp)
            ret, frame = cap.read()
            if selection_area is None:
                selection_area = [0,0, frame.shape[0], frame.shape[1]]

            frame_counter = 0
            while True:
                ret, frame = cap.read()
                frame_counter+=1
                if not ret:
                    break
                tracker, count = process_data(frame, tracker, line_counter, camera_id, name, selection_area)
                if frame_counter % 5 == 0:

                    data = {
                        "camera_id": camera_id,
                        "product_id": product_id,
                        "name": name,
                        "count": count,
                        "timestamp" : time.time()
                    }
                    response = requests.post("http://backend:8543/counting_result/", json=data)
                    if response.status_code == 200:
                        print("Data sent successfully")
                    else:
                        print("Failed to send data")

            cap.release()

    def stop(self):
        if not self.is_running:
            return "No processes to stop"

        self.is_running = False