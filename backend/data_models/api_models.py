
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Camera(BaseModel):
    name: str
    description: Optional[str] = None
    rtsp_stream: Optional[str] = None



class BreadProduct(BaseModel):
    name: str
    photos: Optional[str] = None

class CountRequest(BaseModel):
    camera_id: int
    product_id: int
    selection_area: Optional[str] = None
    counting_line: Optional[str] = None


class CountingResult(BaseModel):
    camera_id: int
    product_id: int
    start_period: datetime
    end_period: datetime
    count: int