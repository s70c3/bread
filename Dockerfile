# Используем базовый образ Python
FROM python:3.9-slim

# Устанавливаем переменную окружения для работы внутри контейнера
ENV PYTHONUNBUFFERED 1

# Создаем директорию для приложения внутри образа
RUN mkdir /app

# Копируем файлы зависимостей и код в директорию приложения
WORKDIR /app
COPY . /app

# Устанавливаем зависимости из requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Команда для запуска сервера uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
