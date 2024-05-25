from fastapi import FastAPI, HTTPException, Depends

from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

import backend.data_models.db_models as models
from backend.data_models.api_models import *
from backend.counting.counting import Producer

app = FastAPI()

producer = Producer()

from backend.data_models.db_models import SessionLocal
from backend.autolabel.worker import label_data


# Функция для получения сессии базы данных
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Подключение к rtsp-потоку
@app.post("/camera/")
def create_camera(camera: Camera, db: Session = Depends(get_db)):
    try:
        db_camera = models.Camera(**camera.dict())
        db.add(db_camera)
        db.commit()
        return {"message": "Camera created successfully"}
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Camera with this name already exists")


# Просмотр списка всех камер
@app.get("/camera/")
def get_cameras(db: Session = Depends(get_db)):
    cameras = db.query(models.Camera).all()
    return {"cameras": cameras}


# Изменение информации о камере
@app.put("/camera/{camera_id}")
def update_camera(camera_id: int, camera: Camera, db: Session = Depends(get_db)):
    db_camera = db.query(models.Camera).filter(models.Camera.camera_id == camera_id).first()
    if db_camera:
        for var, value in vars(camera).items():
            setattr(db_camera, var, value) if value else None
        db.commit()
        return {"message": "Camera updated successfully"}
    raise HTTPException(status_code=404, detail="Camera not found")


# Удаление камеры
@app.delete("/camera/{camera_id}")
def delete_camera(camera_id: int, db: Session = Depends(get_db)):
    db_camera = db.query(models.Camera).filter(models.Camera.camera_id == camera_id).first()
    if db_camera:
        db.delete(db_camera)
        db.commit()
        return {"message": "Camera deleted successfully"}
    raise HTTPException(status_code=404, detail="Camera not found")


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
    db_counting_result = models.CountingResult(**counting_result.dict())
    db.add(db_counting_result)
    db.commit()
    db.refresh(db_counting_result)
    return db_counting_result


@app.get("/stopcount/")
def stop_counting(db: Session = Depends(get_db)):
    producer.stop()


@app.get("/count/")
def start_counting(db: Session = Depends(get_db)):
    streams = [(
        db.query(models.Camera).filter(models.Camera.camera_id == dataset.camera_id).first().rtsp_stream,
        dataset.camera_id,
        dataset.product_id,
        db.query(models.BreadProduct).filter(
            models.BreadProduct.product_id == dataset.product_id).first().name,
        dataset.selection_area,
        dataset.counting_line,
        dataset.status)
        for dataset in db.query(models.CountingRequest).filter(models.CountingRequest.status == 1).all()]

    # Create an instance of the Counting class with all streams

    # Создание экземпляра класса Producer
    producer = Producer(streams)

    # Запуск чтения видео и отправки кадров на обработку
    producer.start()

    return streams


# Просмотр списка всех изделий

@app.get("/count_info/")
def counting_requests_info(db: Session = Depends(get_db)):
    streams = [
        {
            'id':dataset.id,
            'rtsp_stream': db.query(models.Camera).filter(models.Camera.camera_id == dataset.camera_id).first().rtsp_stream,
            'camera_id' : dataset.camera_id,
            'product_id' : dataset.product_id,
            'camera_name': db.query(models.Camera).filter(models.Camera.camera_id == dataset.camera_id).first().name,
            'product_name': db.query(models.BreadProduct).filter(models.BreadProduct.product_id == dataset.product_id).first().name,
            'selection_area': dataset.selection_area,
            'counting_line': dataset.counting_line,
            'status': dataset.status
        }
        for dataset in db.query(models.CountingRequest).all()
    ]

    return streams


# Просмотр списка всех изделий

@app.post("/count/")
def start_new_counting(counting_request: CountingRequest, db: Session = Depends(get_db)):
    new_request = models.CountingRequest(**counting_request.dict())
    db.add(new_request)
    db.commit()
    # Get all streams from the CountRequest table
    if counting_request.status == 0:
        return {"message": "Counting request added, but is not active"}
    # Создание экземпляра класса Producer
    producer.add_stream(
        (db.query(models.Camera).filter(models.Camera.camera_id == counting_request.camera_id).first().rtsp_stream,
         counting_request.camera_id,
         counting_request.product_id,
         db.query(models.BreadProduct).filter(
             models.BreadProduct.product_id == counting_request.product_id).first().name,
         counting_request.selection_area,
         counting_request.counting_line))
    # Запуск чтения видео и отправки кадров на обработку

    return {"message": "Counting started for all streams"}


# Update a counting request
@app.put("/count/{request_id}")
def update_counting_request(request_id: int, counting_request: CountingRequest, db: Session = Depends(get_db)):
    db_counting_request = db.query(models.CountingRequest).filter(models.CountingRequest.id == request_id).first()
    if db_counting_request:
        for var, value in vars(counting_request).items():
            setattr(db_counting_request, var, value) if value else None
        db.commit()
        return {"message": "Counting request updated successfully"}
    raise HTTPException(status_code=404, detail="Counting request not found")

# Delete a counting request
@app.delete("/count/{request_id}")
def delete_counting_request(request_id: int, db: Session = Depends(get_db)):
    db_counting_request = db.query(models.CountingRequest).filter(models.CountingRequest.id == request_id).first()
    if db_counting_request:
        db.delete(db_counting_request)
        db.commit()
        return {"message": "Counting request deleted successfully"}
    raise HTTPException(status_code=404, detail="Counting request not found")

@app.get("/counting_request/{request_id}")
def get_counting_request(request_id: int, db: Session = Depends(get_db)):
    counting_request = db.query(models.CountingRequest).filter(models.CountingRequest.id == request_id).first()
    if counting_request is None:
        raise HTTPException(status_code=404, detail="Counting request not found")

    camera = db.query(models.Camera).filter(models.Camera.camera_id == counting_request.camera_id).first()
    product = db.query(models.BreadProduct).filter(
        models.BreadProduct.product_id == counting_request.product_id).first()

    return {
        'camera_name': camera.name,
        'camera_rtsp': camera.rtsp_stream,
        'product_id': product.product_id,
        'product_name': product.name,
        'status' : counting_request.status
    }


# Просмотр списка всех изделий
@app.get("/bread/")
def get_breads(db: Session = Depends(get_db)):
    breads = db.query(models.BreadProduct).all()
    return {"breads": breads}


# Удаление изделия
@app.delete("/bread/{bread_id}")
def delete_bread(bread_id: int, db: Session = Depends(get_db)):
    db_bread = db.query(models.BreadProduct).filter(models.BreadProduct.product_id == bread_id).first()
    if db_bread:
        db.delete(db_bread)
        db.commit()
        return {"message": "Bread product deleted successfully"}
    raise HTTPException(status_code=404, detail="Bread product not found")


# Подсчет изделий
@app.get("/bread/count/{product_id}")
def count_product(product_id: int, db: Session = Depends(get_db)):
    # Здесь будет логика для подсчета количества изделий
    return {"product_id": product_id, "count": 100}  # Пример ответа, пока без реальной логики


# Просмотр количества изделий за период времени
@app.get("/bread/count/{product_id}/period/{start_date}/{end_date}")
def count_product_period(product_id: int, start_date: str, end_date: str, db: Session = Depends(get_db)):
    start_date = datetime.fromisoformat(start_date)
    end_date = datetime.fromisoformat(end_date)

    count_result = db.query(func.sum(models.CountingResult.count)). \
        filter(models.CountingResult.product_id == product_id). \
        filter(models.CountingResult.timestamp.between(start_date, end_date)).scalar()
    return {"product_id": product_id, "start_date": start_date, "end_date": end_date, "count": count_result}


# Просмотр статистики по конкретному конвейеру (камере)
@app.get("/camera/{camera_id}/period/")
def count_product_period_camera(camera_id: int, start_date: datetime, end_date: datetime,
                                db: Session = Depends(get_db)):
    results = db.query(models.CountingResult.product_id, func.sum(models.CountingResult.count)). \
        filter(models.CountingResult.camera_id == camera_id). \
        filter(models.CountingResult.start_period.between(start_date, end_date)). \
        group_by(models.CountingResult.product_id).all()

    statistics = [{"product_id": product_id, "count": count} for product_id, count in results]
    return {"camera_id": camera_id, "start_date": start_date, "end_date": end_date, "statistics": statistics}
