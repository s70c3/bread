#
FROM python:3.9

#
WORKDIR /code


COPY requirements.txt ./

#
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install roboflow
RUN pip install ultralytics==8.2.16
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y
#
COPY . .

#
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]