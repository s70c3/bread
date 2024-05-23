#
FROM python:3.9

#
WORKDIR /code
#RUN mkdir /root/.cache/autodistill
#RUN wget -P  /root/.cache/autodistill/groundingdino_swint_ogc.pth https://github.com/IDEA-Research/GrouningDINO/releases/download/v0.1.0-alpha/groundingdino_swint_ogc.pth
#RUN wget -P  /root/.cache/autodistill/GroundingDINO_SwinT_OGC.py https://raw.githubusercontent.com/roboflow/GroundingDINO/main/groundingdino/config/GroundingDINO_SwinT_OGC.py


COPY requirements.txt ./

#
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install roboflow
RUN pip install ultralytics==8.2.16
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y
COPY . .

#
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8543"]