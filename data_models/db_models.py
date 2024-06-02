from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import PickleType

from os import environ

Base = declarative_base()

class BreadProduct(Base):
    __tablename__ = 'bread_products'

    product_id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    labeling_name = Column(String, nullable=False)
    photos = Column(String)

    labeling_requests = relationship("LabelingRequest", back_populates="product")
    counting_results = relationship("CountingResult", back_populates="product")

class LabelingRequest(Base):
    __tablename__ = 'labeling_requests'
    product_id = Column(Integer, ForeignKey('bread_products.product_id'), primary_key=True)
    request_id = Column(Integer, ForeignKey('counting_requests.request_id'), primary_key=True)
    name = Column(String)

    request = relationship("CountingRequest", back_populates="request")
    product = relationship("BreadProduct", back_populates="labeling_requests")

class CountingRequest(Base):
    __tablename__ = 'counting_requests'
    request_id = Column(Integer, primary_key=True)

    name = Column(String, nullable=False)
    description = Column(String)
    rtsp_stream = Column(String)

    selection_area = Column(String)
    counting_line = Column(String)
    status = Column(Integer)

    request = relationship("LabelingRequest", back_populates="request")
    labeling_results = relationship("CountingResult",  cascade="all,delete", back_populates="request")

class CountingResult(Base):
    __tablename__ = 'counting_results'

    result_id = Column(Integer, primary_key=True)
    request_id = Column(Integer, ForeignKey('counting_requests.request_id'), nullable=True)
    product_id = Column(Integer, ForeignKey('bread_products.product_id'), nullable=True)
    timestamp = Column(DateTime, nullable=False)
    count = Column(Integer, nullable=False)

    request = relationship("CountingRequest", cascade="all,delete",  back_populates="labeling_results")
    product = relationship("BreadProduct", back_populates="counting_results")

# Указываем параметры подключения к базе данных PostgreSQL
SQLALCHEMY_DATABASE_URL = environ.get("DATABASE_URL")

# Создаем движок базы данных
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Создаем таблицы в базе данных
Base.metadata.create_all(bind=engine)

# Создаем сессию для работы с базой данных
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)