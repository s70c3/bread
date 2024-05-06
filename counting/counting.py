import cv2 # Import OpenCV Library
from ultralytics import YOLO # Import Ultralytics Package

import threading # Threading module import
from ultralytics.solutions import object_counter


class Counting(object):
    def __init__(self, streams, line_points):
        self.models = []
        for stream in streams:
            model = YOLO('../model/yolov8s.pt')  # YOLOv8n Model
            self.models.append(model)

        # Create the tracker thread

        self.counters = []


        self.trackers = []
        for i in range(len(streams)):
            counter = object_counter.ObjectCounter()
            counter.set_args(view_img=True,
                             reg_pts=line_points,
                             classes_names=self.models[i].names,
                             draw_tracks=True,
                             line_thickness=2)
            # Thread used for the video file
            tracker_thread = threading.Thread(target=self._run_tracker_in_thread_,
                                               args=(streams[i], self.models[i], i, line_points),
                                               daemon=True)
            self.trackers.append(tracker_thread)


    def start(self):
        for tracker in self.trackers:
            tracker.start()
            tracker.join()
    def finish(self):
        pass
    def _run_tracker_in_thread_(self, source, model, file_index, counter):
        """
        This function is designed to run a video file or webcam stream
        concurrently with the YOLOv8 model, utilizing threading.

        - source: The path to the video file or the webcam/external
        camera source.
        - model: The file path to the YOLOv8 model.
        - file_index: An argument to specify the count of the
        file being processed.
        """

        video = cv2.VideoCapture(source)  # Read the video file

        while True:
            ret, frame = video.read()  # Read the video frames

            # Exit the loop if no more frames in either video
            if not ret:
                break

            # Track objects in frames if available
            results = model.track(frame, persist=True)
            frame = counter.start_counting(frame, results)
            res_plotted = frame[0].plot()
            cv2.imshow("Tracking_Stream_"+str(file_index), res_plotted)

            key = cv2.waitKey(1)
            if key == ord('q'):
                break

        # Release video sources
        video.release()

