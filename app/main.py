from fastapi import FastAPI, HTTPException, Path, Query
from pydantic import BaseModel
from datetime import datetime
import sqlite3

app = FastAPI()

# Модель для камер видеонаблюдения
class Camera(BaseModel):
    name: str
    description: str
    rtsp_stream: str
    selection_area: str
    counting_line: str

# Модель для хлебобулочных изделий
class BreadProduct(BaseModel):
    name: str
    photos: str
    video: str

# Функция подключения к базе данных
def connect_db():
    return sqlite3.connect("counting_system.db")

# Подключение к rtsp-потоку
@app.post("/cameras/")
def create_camera(camera: Camera):
    conn = connect_db()
    c = conn.cursor()
    c.execute("INSERT INTO cameras (name, description, rtsp_stream, selection_area, counting_line) VALUES (?, ?, ?, ?, ?)",
              (camera.name, camera.description, camera.rtsp_stream, camera.selection_area, camera.counting_line))
    conn.commit()
    conn.close()
    return {"message": "Camera created successfully"}

# Просмотр списка всех камер
@app.get("/cameras/")
def get_cameras():
    conn = connect_db()
    c = conn.cursor()
    c.execute("SELECT * FROM cameras")
    cameras = c.fetchall()
    conn.close()
    return {"cameras": cameras}

# Изменение информации о камере
@app.put("/cameras/{camera_id}")
def update_camera(camera_id: int, camera: Camera):
    conn = connect_db()
    c = conn.cursor()
    c.execute("UPDATE cameras SET name=?, description=?, rtsp_stream=?, selection_area=?, counting_line=? WHERE camera_id=?",
              (camera.name, camera.description, camera.rtsp_stream, camera.selection_area, camera.counting_line, camera_id))
    conn.commit()
    conn.close()
    return {"message": "Camera updated successfully"}

# Удаление камеры
@app.delete("/cameras/{camera_id}")
def delete_camera(camera_id: int):
    conn = connect_db()
    c = conn.cursor()
    c.execute("DELETE FROM cameras WHERE camera_id=?", (camera_id,))
    conn.commit()
    conn.close()
    return {"message": "Camera deleted successfully"}

# Подсчет изделий
@app.get("/bread/count/{product_id}")
def count_product(product_id: int):
    # Здесь будет логика для подсчета количества изделий
    return {"product_id": product_id, "count": 100}  # Пример ответа, пока без реальной логики

# Просмотр количества изделий за период времени
@app.get("/bread/count/{product_id}/period/")
def count_product_period(product_id: int, start_date: datetime, end_date: datetime):
    conn = connect_db()
    c = conn.cursor()
    c.execute("SELECT SUM(count) FROM counting_results WHERE product_id=? AND start_period BETWEEN ? AND ?",
              (product_id, start_date, end_date))
    count_result = c.fetchone()[0]
    conn.close()
    return {"product_id": product_id, "start_date": start_date, "end_date": end_date, "count": count_result}


# Просмотр статистики по конкретному конвейеру (камере)
@app.get("/camera/{camera_id}/period/")
def count_product_period_camera(camera_id: int, start_date: datetime, end_date: datetime):
    conn = connect_db()
    c = conn.cursor()
    c.execute(
        "SELECT product_id, SUM(count) FROM counting_results WHERE camera_id=? AND start_period BETWEEN ? AND ? GROUP BY product_id",
        (camera_id, start_date, end_date))
    results = c.fetchall()
    statistics = []
    for result in results:
        product_id, count = result
        statistics.append({"product_id": product_id, "count": count})
    conn.close()
    return {"camera_id": camera_id, "start_date": start_date, "end_date": end_date, "statistics": statistics}