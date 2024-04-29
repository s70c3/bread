import os
import sqlite3

# Подключение к базе данных
# Проверка существования файла базы данных
db_filename = 'counting_system.db'
if os.path.isfile(db_filename):
    print("База данных уже существует.")
else:
    # Создание новой базы данных
    conn = sqlite3.connect(db_filename)
    c = conn.cursor()

# Создание таблицы для камер видеонаблюдения
c.execute('''CREATE TABLE IF NOT EXISTS cameras (
             camera_id INTEGER PRIMARY KEY,
             name TEXT NOT NULL,
             description TEXT,
             rtsp_stream TEXT,
             selection_area TEXT,
             counting_line TEXT
             )''')

# Создание таблицы для хлебобулочных изделий
c.execute('''CREATE TABLE IF NOT EXISTS bread_products (
             product_id INTEGER PRIMARY KEY,
             name TEXT NOT NULL,
             photos BLOB,
             video BLOB
             )''')

# Создание таблицы для хранения результатов подсчета
c.execute('''CREATE TABLE IF NOT EXISTS counting_results (
             result_id INTEGER PRIMARY KEY,
             camera_id INTEGER NOT NULL,
             product_id INTEGER NOT NULL,
             start_period DATETIME NOT NULL,
             end_period DATETIME NOT NULL,
             count INTEGER NOT NULL,
             FOREIGN KEY (camera_id) REFERENCES cameras (camera_id),
             FOREIGN KEY (product_id) REFERENCES bread_products (product_id)
             )''')

# Сохранение изменений и закрытие подключения
conn.commit()
conn.close()
