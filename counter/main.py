from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel

from typing import List, Tuple

import uvicorn
from sqlalchemy.orm import Session

from counter.producer import Producer
from data_models.api_models import CountingRequest, Process
import  data_models.db_models as models
import multiprocessing as mp

from data_models.db_models import SessionLocal

app = FastAPI()

# Функция для получения сессии базы данных
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

processes = []
process_ids = []




@app.on_event("startup")
async def startup_event():
    db = next(get_db())
    video_sources =  [(
        db.query(models.Camera).filter(models.Camera.camera_id == dataset.camera_id).first().rtsp_stream,
        dataset.camera_id,
        dataset.product_id,
        db.query(models.BreadProduct).filter(
            models.BreadProduct.product_id == dataset.product_id).first().name,
        dataset.selection_area,
        dataset.counting_line,
        dataset.status)
        for dataset in db.query(models.CountingRequest).filter(models.CountingRequest.status == 1).all()]
    for video_source in video_sources:
        producer = Producer(video_source)
        process = mp.Process(target=producer.start)
        process.start()
        processes.append(process)
        process_ids.append(process.pid)
    return {"process_ids": process_ids}

@app.post("/processes/")
def create_processes(video_sources: List[Tuple[str]]):
    process_ids = []
    for video_source in video_sources:
        producer = Producer(video_source)
        process = mp.Process(target=producer.start)
        process.start()
        new_process = Process(id=process.pid, command=str(video_source), status="running")
        processes.append(new_process)
        process_ids.append(process.pid)
    return {"process_ids": process_ids}

@app.post("/processes/")
def create_processes(video_sources: List[Tuple[str]]):
    process_ids = []
    for video_source in video_sources:
        process = mp.Process(target=Producer(list(video_source)).start)
        process.start()
        new_process = Process(id=process.pid, command=str(video_source), status="running")
        processes.append(new_process)
        process_ids.append(process.pid)
    return {"process_ids": process_ids}

@app.post("/process/")
def create_process(video_source):
    producer = Producer(video_source)
    process = mp.Process(target=producer.start)
    process.start()
    new_process = Process(id=process.pid, command=str(video_source), status="running")
    processes.append(new_process)
    return {"process_id": process.pid}

@app.get("/process/{process_id}")
def get_process(process_id: int):
    for process in processes:
        if process.id == process_id:
            return process
    raise HTTPException(status_code=404, detail="Process not found")

@app.delete("/process/{process_id}")
def delete_process(process_id: int):
    for process in processes:
        if process.id == process_id:
            process.kill()
            processes.remove(process)
            return {"message": "Process killed successfully"}
    raise HTTPException(status_code=404, detail="Process not found")

@app.get("/processes/")
def get_processes():
    return {"process_ids": process_ids}

