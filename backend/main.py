from fastapi import FastAPI, HTTPException, Depends

from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

import backend.data_models.db_models as models
from backend.data_models.api_models import *

app = FastAPI()

from backend.data_models.db_models import SessionLocal


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
    print(**bread.dict())
    try:
        db_bread = models.BreadProduct(**bread.dict())
        db.add(db_bread)
        db.commit()
        return {"message": "Bread product created successfully"}
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Bread product with this name already exists")



# Создание нового изделия
@app.post("/label/")
def create_dataset(dataset: CountRequest, db: Session = Depends(get_db)):
    stream = db.query(models.Camera).filter(models.Camera.camera_id == dataset.camera_id).first().scalar()
    bread = db.query(models.BreadProduct).filter(models.BreadProduct.product_id == dataset.bread_id).first().scalar()
    print(bread, stream)

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
@app.get("/bread/count/{product_id}/period/")
def count_product_period(product_id: int, start_date: datetime, end_date: datetime, db: Session = Depends(get_db)):
    count_result = db.query(func.sum(models.CountingResult.count)). \
        filter(models.CountingResult.product_id == product_id). \
        filter(models.CountingResult.start_period.between(start_date, end_date)).scalar()
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
