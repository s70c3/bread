
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class BreadProduct(BaseModel):
    name: str
    labeling_name: Optional[str] = None
    photos: Optional[List[str]] = None

class CountingRequest(BaseModel):
    name: str
    description: Optional[str] = None
    rtsp_stream: Optional[str] = None
    selection_area: Optional[str] = None
    counting_line: Optional[str] = None
    status : int


class LabelingRequest(BaseModel):
    count_id: int
    product_id: int
    name: str


class CountingResult(BaseModel):
    request_id: int
    product_id: int
    timestamp: datetime
    count: int


class Process(BaseModel):
    id: int
    command: str
    status: str
