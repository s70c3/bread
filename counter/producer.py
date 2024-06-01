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
            self.video_source = ()
        else:
            self.video_source = video_source
        self.is_running = False

    def start(self):
        if self.is_running:
            return "Процесс уже запущен."
        self.is_running = True
        self.add_stream(*self.video_source)


    def add_stream(self,  rtsp, request_id, selection_area, counting_line, status):
        # create instance of BoxAnnotator and LineCounterAnnotator
        mapping = dict()
        # try:
        response = requests.get('http://backend:8543/bread/')
        breads = response.json()['breads']
        if len(breads)>0:
            for product in breads:
                mapping[product['labeling_name']] = product['product_id']
        else:
            mapping=None
        counting_line = ast.literal_eval(counting_line)
        selection_area = ast.literal_eval(selection_area)
        LINE_START = sv.Point(counting_line[0] - selection_area[1], counting_line[1])
        LINE_END = sv.Point(counting_line[2] - selection_area[1], counting_line[3])
        if status == 0:
            return
        line_counter = sv.LineZone(start=LINE_START, end=LINE_END)
        tracker = sv.ByteTrack()

        self._read_video(rtsp, tracker, line_counter, request_id, selection_area, mapping)

    def _read_video(self, rtsp, tracker, line_counter, request_id=1, selection_area=None, mapping = None):
            cap = cv2.VideoCapture(rtsp)
            ret, frame = cap.read()

            if selection_area is None:
                selection_area = [0,0, frame.shape[0], frame.shape[1]]
            frame_counter = 0
            model = YOLO('/model/yolo.pt')
            zero_frames = 0
            current_class = "empty"
            while self.is_running:
                ret, frame = cap.read()
                if not ret:
                    print("Can't receive frame. Retrying ...")
                    cap.release()
                    cap = cv2.VideoCapture(rtsp)
                    ret, frame = cap.read()

                frame_counter+=1
                tracker, line_counter, current_class, zero_frames, need_to_store = process_data(frame, model, tracker, line_counter,
                                                                                  selection_area,
                                                                                 current_class, zero_frames)
                if frame_counter % 20 == 0 or need_to_store:

                    if need_to_store:
                        current_class_save = need_to_store[0]
                        count_value = need_to_store[1]
                    else:
                        current_class_save = current_class
                        count_value = line_counter.out_count

                    if current_class_save == "empty":
                        product_id = -1
                    else:
                        product_id =  mapping[current_class_save] if mapping else current_class_save

                    data = {
                        "request_id": request_id,
                        "product_id": product_id,
                        "count": count_value,
                        "timestamp" : time.time()
                    }
                    response = requests.post("http://backend:8543/counting_result/", json=data)
                    if response.status_code == 200:
                        print("Data sent successfully: "+ str(request_id) + " " + str(product_id) + " " +str(count_value))
                    else:
                        print("Failed to send data")
                        print(response.text)
            else:
                cap.release()

    def stop(self):
        if not self.is_running:
            return "No processes to stop"
        print("Stopping process")
        self.is_running = False