import requests
from fastapi import FastAPI, HTTPException, Depends

from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

import data_models.db_models as models
from data_models.api_models import *

app = FastAPI()

from data_models.db_models import SessionLocal
from backend.autolabel.worker import label_data

from datetime import datetime, timedelta

# Функция для получения сессии базы данных
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def get_main():
    return {"message": "Welcome to the Bread Counter API"}
# Просмотр списка всех изделий
@app.get("/bread/")
def get_breads(db: Session = Depends(get_db)):
    breads = db.query(models.BreadProduct).all()
    return {"breads": breads}


# Создание нового изделия
@app.post("/bread/")
def create_bread(bread: BreadProduct, db: Session = Depends(get_db)):
    try:
        db_bread = models.BreadProduct(**bread.dict())
        db.add(db_bread)
        db.commit()
        return {"message": "Bread product created successfully"}
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Bread product with this name already exists")


@app.put("/bread/{product_id}")
def update_product(product_id: int, product: BreadProduct, db: Session = Depends(get_db)):
    db_product = db.query(models.BreadProduct).filter(models.BreadProduct.product_id == product_id).first()
    if db_product:
        for var, value in vars(product).items():
            setattr(db_product, var, value) if value else None
        db.commit()
        return {"message": "Продукт успешно обновлен."}
    raise HTTPException(status_code=404, detail="Продукт не найден.")


# Удаление изделия
@app.delete("/bread/{bread_id}")
def delete_bread(bread_id: int, db: Session = Depends(get_db)):
    db_bread = db.query(models.BreadProduct).filter(models.BreadProduct.product_id == bread_id).first()
    if db_bread:
        db.delete(db_bread)
        db.commit()
        return {"message": "Bread product deleted successfully"}
    raise HTTPException(status_code=404, detail="Bread product not found")


# Создание нового изделия
@app.post("/label/")
def create_dataset(dataset: LabelingRequest, db: Session = Depends(get_db)):
    stream = db.query(models.Camera).filter(models.Camera.camera_id == dataset.camera_id).first().rtsp_stream
    bread = db.query(models.BreadProduct).filter(models.BreadProduct.product_id == dataset.product_id).first().name

    # Start the label_data task in Celery
    task = label_data.delay(stream, dataset.camera_id, dataset.product_id, bread)

    return {"message": "Task started", "task_id": str(task.id)}


@app.post("/counting_result/")
def create_counting_result(counting_result: CountingResult, db: Session = Depends(get_db)):
    if counting_result.product_id == -1:
        counting_result.product_id = None
    db_counting_result = models.CountingResult(**counting_result.dict())
    db.add(db_counting_result)
    db.commit()
    db.refresh(db_counting_result)
    return db_counting_result


# Просмотр списка всех изделий

@app.get("/count/")
def counting_requests_info(db: Session = Depends(get_db)):
    streams = [
        {
            'request_id': counting_request.request_id,
            'rtsp_stream': counting_request.rtsp_stream,
            'name': counting_request.name,
            'description': counting_request.description,
            'selection_area': counting_request.selection_area,
            'counting_line': counting_request.counting_line,
            'status': counting_request.status
        }
        for counting_request in db.query(models.CountingRequest).all()
    ]

    return streams


# Просмотр списка всех изделий

@app.post("/count/")
def start_new_counting(counting_request: CountingRequest, db: Session = Depends(get_db)):

    new_request = models.CountingRequest(**counting_request.dict())
    db.add(new_request)
    db.commit()

    request_id = new_request.request_id
    # Get all st    reams from the CountRequest table
    if counting_request.status == 0:
        return {"message": "Запрос на подсчёт  создан, но не активен"}
    # Запуск чтения видео и отправки кадров на обработку

    response = requests.post(f'http://counter:8544/process/', json={
        'request_id': request_id,
        'rtsp_stream': counting_request.rtsp_stream,
        'name': counting_request.name,
        'description': counting_request.description,
        'selection_area': counting_request.selection_area,
        'counting_line': counting_request.counting_line,
        'status': counting_request.status
    })
    if response.status_code == 200:
        return {"message": "Counting request updated successfully"}
    else:
        raise HTTPException(status_code=response.status_code, detail=response.text)


# Update a counting request
@app.put("/count/{request_id}")
def update_counting_request(request_id: int, counting_request: CountingRequest, db: Session = Depends(get_db)):
    db_counting_request = db.query(models.CountingRequest).filter(models.CountingRequest.request_id == request_id).first()
    pre_status = db_counting_request.status
    if db_counting_request:
        for var, value in vars(counting_request).items():
            setattr(db_counting_request, var, value) if value is not None else None
        db.commit()
        if pre_status == 1:
            response = requests.delete(f'http://counter:8544/process/{request_id}')
        if counting_request.status == 1:
            response = requests.post(f'http://counter:8544/process/', json={
                'request_id' : request_id,
                'rtsp_stream': counting_request.rtsp_stream,
                'name' : counting_request.name,
                'description' : counting_request.description,
                'selection_area': counting_request.selection_area,
                'counting_line': counting_request.counting_line,
                'status': counting_request.status
            })
            if response.status_code == 200:
                return {"message": "Counting request updated successfully"}
            else:
                raise HTTPException(status_code=response.status_code, detail=response.text)





# Delete a counting request
@app.delete("/count/{request_id}")
def delete_counting_request(request_id: int, db: Session = Depends(get_db)):
    db_counting_request = db.query(models.CountingRequest).filter(models.CountingRequest.request_id == request_id).first()
    if db_counting_request:
        response = requests.delete(f'http://counter:8544/process/{request_id}')
        db.delete(db_counting_request)
        db.commit()
        return {"message": "Counting request deleted successfully"}
    raise HTTPException(status_code=404, detail="Counting request not found")


@app.get("/counting_request/{request_id}")
def get_counting_request(request_id: int, db: Session = Depends(get_db)):
    counting_request = db.query(models.CountingRequest).filter(models.CountingRequest.request_id == request_id).first()
    if counting_request is None:
        raise HTTPException(status_code=404, detail="Counting request not found")

    camera = db.query(models.Camera).filter(models.Camera.camera_id == counting_request.camera_id).first()

    return {
        'camera_name': camera.name,
        'camera_rtsp': camera.rtsp_stream,
        'status': counting_request.status
    }


@app.get("/aggregate/")
def aggregate_production(
    start_period: datetime,
    end_period: datetime,
    step: int,
    request_id: int,
    db: Session = Depends(get_db)
):
    try:
        results = []
        current_period_start = start_period

        while current_period_start < end_period:
            current_period_end = current_period_start + timedelta(minutes=step)
            query = db.query(
                models.CountingResult.product_id,
                func.sum(models.CountingResult.count).label('total_count')
            ).filter(
                models.CountingResult.request_id == request_id,
                models.CountingResult.timestamp >= current_period_start,
                models.CountingResult.timestamp < current_period_end
            ).group_by(models.CountingResult.product_id)

            period_results = query.all()

            for result in period_results:
                product_id = result.product_id
                if product_id is None:
                    product_id = "Conveyor Idle"
                results.append({
                    "period_start": current_period_start,
                    "period_end": current_period_end,
                    "product_id": product_id,
                    "total_count": result.total_count
                })

            current_period_start = current_period_end

        return {"aggregated_results": results}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
# Просмотр количества изделий за период времени
@app.get("/bread/count/{camera_id}/period/{start_date}/{end_date}")
def count_product_period(camera_id: int, start_date: str, end_date: str, db: Session = Depends(get_db)):
    start_date = datetime.fromisoformat(start_date)
    end_date = datetime.fromisoformat(end_date)
    start_count = db.query(func.max(models.CountingResult.count)). \
                       filter(models.CountingResult.camera_id == camera_id). \
                       filter(models.CountingResult.timestamp.between(start_date, end_date)).scalar() or 0
    end_count = db.query(
        func.min(models.CountingResult.count)). \
                    filter(models.CountingResult.camera_id == camera_id). \
                    filter(models.CountingResult.timestamp.between(start_date, end_date)).scalar() or 0
    count_result = start_count - end_count
    return {"camera_id": camera_id, "start_date": start_date, "end_date": end_date, "count": count_result}

