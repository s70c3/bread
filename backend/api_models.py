
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Camera(BaseModel):
    camera_id: int
    name: str
    description: Optional[str] = None
    rtsp_stream: Optional[str] = None
    selection_area: Optional[str] = None
    counting_line: Optional[str] = None


class BreadProduct(BaseModel):
    product_id: int
    name: str
    photos: Optional[str] = None
    video: Optional[str] = None

class CountingResult(BaseModel):
    result_id: int
    camera_id: int
    product_id: int
    start_period: datetime
    end_period: datetime
    count: int