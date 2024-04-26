from typing import List, Dict, Optional
from fastapi import FastAPI, HTTPException, File, UploadFile
from pydantic import BaseModel
from datetime import datetime
from collections import defaultdict

app = FastAPI(
    title="Bread and Camera API",
    description="API for managing bread types, counting breads, and managing cameras.",
    version="1.0",
    openapi_tags=[
        {"name": "Breads", "description": "Endpoints for managing bread types."},
        {"name": "Bread Counts", "description": "Endpoints for counting breads."},
        {"name": "Cameras", "description": "Endpoints for managing cameras."},
    ],
)

class BreadType(BaseModel):
    name: str
    enabled: bool = True
    image: str

class BreadCounting(BaseModel):
    start_time: datetime
    end_time: datetime
    bread_type: str
    counting_value: int

class Camera(BaseModel):
    link: str
    conveyor_number: int
    description: Optional[str]
    area: List[int]
    line: List[int]

# Stub data for breads
breads: Dict[str, BreadType] = {
    "white_bread": BreadType(name="white_bread", image="white_bread.jpg"),
    "whole_grain_bread": BreadType(name="whole_grain_bread", image="whole_grain_bread.jpg")
}

# Stub data for cameras
cameras: Dict[int, Camera] = {
    1: Camera(link="http://example.com/camera1", conveyor_number=1, description="Camera 1 description", area=[0, 0, 100, 100], line=[0, 0, 100, 100]),
    2: Camera(link="http://example.com/camera2", conveyor_number=2, description="Camera 2 description", area=[0, 0, 100, 100], line=[0, 0, 100, 100])
}

statistics = []

@app.post("/bread/", response_model=BreadType, tags=["Breads"])
async def create_bread(name: str, image: UploadFile = File(...)):
    bread = BreadType(name=name, image=image.filename)
    # Save bread image to the server's filesystem
    with open(image.filename, "wb") as buffer:
        buffer.write(image.file.read())
    return bread

@app.get("/bread/", response_model=List[BreadType], tags=["Breads"])
async def get_breads():
    return [bread for bread in breads.values() if bread.enabled]

@app.get("/breads/{bread_name}/", response_model=BreadType, tags=["Breads"])
async def get_bread(bread_name: str):
    if bread_name not in breads:
        raise HTTPException(status_code=404, detail="Bread not found")
    return breads[bread_name]

@app.put("/breads/{bread_name}/", response_model=BreadType, tags=["Breads"])
async def update_bread(bread_name: str, enabled: Optional[bool] = None):
    if bread_name not in breads:
        raise HTTPException(status_code=404, detail="Bread not found")
    if enabled is not None:
        breads[bread_name].enabled = enabled
    return breads[bread_name]

@app.delete("/breads/{bread_name}/", response_model=BreadType, tags=["Breads"])
async def delete_bread(bread_name: str):
    if bread_name not in breads:
        raise HTTPException(status_code=404, detail="Bread not found")
    deleted_bread = breads.pop(bread_name)
    return deleted_bread

@app.post("/count/", response_model=BreadCounting, tags=["Bread Counts"])
async def count_bread(bread_name: str, counting_value: int, start_timestamp : datetime, end_timestamp : datetime):
    if bread_name not in breads:
        raise HTTPException(status_code=404, detail="Bread type not found")
    if not breads[bread_name].enabled:
        raise HTTPException(status_code=400, detail="Bread type is disabled")

    return BreadCounting(bread_type=bread_name, counting_value=counting_value,  start_time=start_timestamp,
        end_time=end_timestamp)

@app.get("/count/", response_model=BreadCounting, tags=["Bread Counts"])
async def get_count(bread_name: str, start_timestamp : datetime, duration : int):
    if bread_name not in breads:
        raise HTTPException(status_code=404, detail="Bread type not found")
    if not breads[bread_name].enabled:
        raise HTTPException(status_code=400, detail="Bread type is disabled")

    return 1000

@app.post("/cameras/", response_model=Camera, tags=["Cameras"])
async def create_camera(camera: Camera):
    camera_id = len(cameras) + 1
    cameras[camera_id] = camera
    return camera

@app.get("/cameras/", response_model=List[Camera], tags=["Cameras"])
async def get_cameras():
    return list(cameras.values())

@app.put("/cameras/{camera_id}/", response_model=Camera, tags=["Cameras"])
async def update_camera(camera_id: int, camera: Camera):
    if camera_id not in cameras:
        raise HTTPException(status_code=404, detail="Camera not found")
    cameras[camera_id] = camera
    return camera

@app.delete("/cameras/{camera_id}/", response_model=Camera, tags=["Cameras"])
async def delete_camera(camera_id: int):
    if camera_id not in cameras:
        raise HTTPException(status_code=404, detail="Camera not found")
    deleted_camera = cameras.pop(camera_id)
    return deleted_camera


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
