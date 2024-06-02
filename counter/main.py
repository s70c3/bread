from fastapi import FastAPI, HTTPException, Depends
import requests
from pydantic import BaseModel

from typing import List, Tuple

import uvicorn
from sqlalchemy.orm import Session

from counter.producer import Producer
from data_models.api_models import CountingRequest, Process
import data_models.db_models as models
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
    response = requests.get("http://backend:8543/count/")
    counting_requests = response.json()
    video_sources = [(
        counting_request['request_id'],
        counting_request['rtsp_stream'],
        counting_request['selection_area'],
        counting_request['counting_line'],
        counting_request['status'])
        for counting_request in counting_requests if counting_request['status'] == 1]
    for video_source in video_sources:
        producer = Producer(video_source)
        process = mp.Process(target=producer.start)
        process.start()
        processes.append(process)
        process_ids[str(video_source[0])] = process.pid
    return process_ids


@app.post("/process/")
def create_process(request_id, counting_request: CountingRequest):
    video_source = (counting_request.request_id,
                    counting_request.rtsp_stream,
                    counting_request.selection_area,
                    counting_request.counting_line,
                    counting_request.status)

    producer = Producer(video_source)
    process = mp.Process(target=producer.start)
    process.start()
    processes.append(process)
    process_ids[str(request_id)] = process.pid
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
    try:
        process_id = process_ids[str(request_id)]
    except KeyError:
        raise HTTPException(status_code=404, detail="Process not found")
    for process in processes:
        if process.pid == process_id:
            process.kill()
            processes.remove(process)
            process_ids.pop(str(request_id))
            return {"message": "Process killed successfully"}
    raise HTTPException(status_code=404, detail="Process not found")


@app.get("/processes/")
def get_processes():
    return process_ids
