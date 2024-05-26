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
process_ids = dict()




@app.on_event("startup")
async def startup_event():
    db = next(get_db())
    video_sources =  [(
        dataset.id,
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
        producer = Producer(video_source[1:])
        process = mp.Process(target=producer.start)
        process.start()
        processes.append(process)
        process_ids[int(video_source[0])]=process.pid
    return process_ids

@app.post("/process/")
def create_process(counting_request: CountingRequest, db: Session = Depends(get_db)):
    video_source = (counting_request.id,
    db.query(models.Camera).filter(models.Camera.camera_id == counting_request.camera_id).first().rtsp_stream,
    counting_request.camera_id,
    counting_request.product_id,
    db.query(models.BreadProduct).filter(
        models.BreadProduct.product_id == counting_request.product_id).first().name,
    counting_request.selection_area,
    counting_request.counting_line,
    counting_request.status)
    producer = Producer(video_source[1:])
    process = mp.Process(target=producer.start)
    process.start()
    processes.append(process)
    process_ids[video_source[0]]=process.pid
    return process_ids

@app.get("/process/{request_id}")
def get_process(request_id: int):
    process_id = process_ids[request_id]
    for process in processes:
        if process.pid == process_id:
            return process
    raise HTTPException(status_code=404, detail="Process not found")

@app.delete("/process/{request_id}")
def delete_process(request_id: int):
    process_id = process_ids[request_id]
    for process in processes:
        if process.pid == process_id:
            process.kill()
            processes.remove(process)
            process_ids.pop(request_id)
            return {"message": "Process killed successfully"}
    raise HTTPException(status_code=404, detail="Process not found")

@app.get("/processes/")
def get_processes():
    return process_ids

