from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from os import environ

Base = declarative_base()

class Camera(Base):
    __tablename__ = 'cameras'

    camera_id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)
    rtsp_stream = Column(String)

    counting_results = relationship("CountingResult", back_populates="camera")
    counting_requests = relationship("CountingRequest", back_populates="camera")


class BreadProduct(Base):
    __tablename__ = 'bread_products'

    product_id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    photos = Column(String)

    counting_results = relationship("CountingResult", back_populates="product", overlaps="counting_requests")
    counting_requests = relationship("CountingRequest", back_populates="product", overlaps="counting_results")


class CountingRequest(Base):
    __tablename__ = 'counting_requests'
    product_id = Column(Integer, ForeignKey('bread_products.product_id'), primary_key=True)
    camera_id = Column(Integer, ForeignKey('cameras.camera_id'), primary_key=True)
    name = Column(String, nullable=False)
    selection_area = Column(String)
    counting_line = Column(String)

    camera = relationship("Camera", back_populates="counting_requests")
    product = relationship("BreadProduct", back_populates="counting_requests")


class CountingResult(Base):
    __tablename__ = 'counting_results'

    result_id = Column(Integer, primary_key=True)
    camera_id = Column(Integer, ForeignKey('cameras.camera_id'), nullable=False)
    product_id = Column(Integer, ForeignKey('bread_products.product_id'), nullable=False)
    start_period = Column(DateTime, nullable=False)
    end_period = Column(DateTime, nullable=False)
    count = Column(Integer, nullable=False)

    camera = relationship("Camera", back_populates="counting_results")
    product = relationship("BreadProduct", back_populates="counting_results")

# Указываем параметры подключения к базе данных PostgreSQL
SQLALCHEMY_DATABASE_URL = environ.get("DATABASE_URL")

# Создаем движок базы данных
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Создаем таблицы в базе данных
Base.metadata.create_all(bind=engine)

# Создаем сессию для работы с базой данных
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)