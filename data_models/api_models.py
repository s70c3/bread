
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class Camera(BaseModel):
    name: str
    description: Optional[str] = None
    rtsp_stream: Optional[str] = None

class BreadProduct(BaseModel):
    name: str
    photos: Optional[List[str]] = None

class CountingRequest(BaseModel):
    camera_id: int
    product_id: int
    selection_area: Optional[str] = None
    counting_line: Optional[str] = None
    status : int


class LabelingRequest(BaseModel):
    camera_id: int
    product_id: int
    name: str


class CountingResult(BaseModel):
    camera_id: int
    product_id: int
    timestamp: datetime
    count: int


class Process(BaseModel):
    id: int
    command: str
    status: str
