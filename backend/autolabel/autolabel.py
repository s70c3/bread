import supervision as sv
from tqdm.notebook import tqdm
import cv2
# from autodistill_grounded_sam import GroundedSAM
from autodistill_grounding_dino import GroundingDINO
from autodistill.detection import CaptionOntology
from ultralytics import YOLO

def create_images(video_stream, conveyor, dist):
    cap = cv2.VideoCapture(video_stream)

    FRAME_STRIDE = 30
    image_name_pattern = str(conveyor) + "-{:05d}.png"
    with sv.ImageSink(target_dir_path=dist, image_name_pattern=image_name_pattern) as sink:
        for image in sv.get_video_frames_generator(source_path=str(video_stream), stride=FRAME_STRIDE):
            image = cv2.resize(image, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_LINEAR)
            sink.save_image(image=image)

    return dist

def label(source, dist,  name="bread",  is_packed = False):
    if not is_packed:
        ontology = CaptionOntology({
            "conveyor": "conveyor",
            "bread": name,
        })
    else:
        ontology = CaptionOntology({
            "conveyor": "conveyor",
            "packed bread": name,
        })

    base_model = GroundingDINO(ontology=ontology)
    DATASET_DIR_PATH = str(dist)

    dataset = base_model.label(
        input_folder= source,
        extension=".png",
        output_folder=DATASET_DIR_PATH)

    return DATASET_DIR_PATH

def train_yolo(dataset_dir, name):
    DATA_YAML_PATH = f"{dataset_dir}/data.yaml"
    target_model = YOLO("yolov8m.pt")
    target_model.train(data=DATA_YAML_PATH, epochs=100, imgsz=640, name=name)

    # Export the model to ONNX format
    success = target_model.export(format='onnx')

    return True
