from celery import Celery
import streamlit as st
# Initialize Celery
import os
broker_url = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379")
app = Celery('autolabel', broker=broker_url)

def show_worker_status():
    i = app.control.inspect()

    # Show active tasks
    st.write('Текущие задачи по обучению')
    st.write(i.active())

    # Show reserved tasks
    st.write('Запланированные задачи по обучению:')
    st.write(i.reserved())

    # Show registered tasks
    st.write('Зарегистрированные задачи:')
    st.write(i.registered())