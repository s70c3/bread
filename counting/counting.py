import cv2 # Import OpenCV Library
from ultralytics import YOLO # Import Ultralytics Package

import threading # Threading module import
import supervision as sv


class Counting(object):
    def __init__(self, streams, line_points=[(0, 2000), (3000, 2000)]):
        self.models = []
        # settings
        LINE_START = sv.Point(0, 2000)
        LINE_END = sv.Point(3000, 2000)

        for stream in streams:
            model = YOLO('../model/yolo.pt')  # YOLOv8n Model
            self.models.append(model)

        # Create the tracker thread

        self.counters = []


        self.trackers = []
        for i in range(len(streams)):
            tracker = sv.ByteTrack()

            line_counter = sv.LineZone(start=LINE_START, end=LINE_END)
            # create instance of BoxAnnotator and LineCounterAnnotator
            line_annotator = sv.LineZoneAnnotator(thickness=4, text_thickness=4, text_scale=2)

            tracker_thread = threading.Thread(target=self._run_tracker_in_thread_,
                                               args=(streams[i], self.models[i], i, tracker, line_counter, line_annotator),
                                               daemon=True)
            self.trackers.append(tracker_thread)


    def start(self):
        for tracker in self.trackers:
            tracker.start()
        for tracker in self.trackers:
            tracker.join()

    def finish(self):
        pass
    def _run_tracker_in_thread_(self, source, model, file_index, tracker, line_counter, line_annotator):
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
        # cv2.namedWindow("preview"+str(file_index), cv2.WINDOW_NORMAL)
        while True:
            ret, frame = video.read()  # Read the video frames
            # Exit the loop if no more frames in either video
            if not ret:
                break

            # Track objects in frames if available
            results = model(frame)[0]
            # frame = counter.start_counting(frame, results)
            detections = sv.Detections.from_ultralytics(results)
            detections = tracker.update_with_detections(detections)

            # updating line counter
            line_counter.trigger(detections=detections)

            line_annotator.annotate(frame=frame, line_counter=line_counter)
            print(file_index, line_counter.out_count)

            frame = cv2.resize(frame, None, fx=0.25, fy=0.25, interpolation=cv2.INTER_LINEAR)
            # cv2.imshow("Thread"+str(file_index),frame)
            #
            # key = cv2.waitKey(1)
            # if key == ord('q'):
            #     break
            # ret, buffer = cv2.imencode('.jpg', frame)
            # frame = buffer.tobytes()
            # yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


            # Release video sources
        video.release()

c = Counting(['/Users/s70c3/Projects/breadProduct/video/20240412_184850.mp4',
             '/Users/s70c3/Projects/breadProduct/video/20240413_090449.mp4'])
c.start()



