# Export the model
from ultralytics import YOLO
model = YOLO("/Users/s70c3/Projects/breadProduct/model/yolo.pt")
model.export(format="onnx")
