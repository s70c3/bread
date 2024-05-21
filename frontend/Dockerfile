FROM python:3.11

COPY requirements.txt app/requirements.txt
WORKDIR /app

RUN pip install -r requirements.txt
RUN pip install supervision
RUN pip install streamlit_drawable_canvas
RUN pip install celery
COPY . /app

EXPOSE 8501

ENTRYPOINT ["streamlit","run"]

CMD ["app.py"]
