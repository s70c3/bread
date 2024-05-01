from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import  sessionmaker,relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Camera(Base):
    __tablename__ = 'cameras'

    camera_id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)
    rtsp_stream = Column(String)
    selection_area = Column(String)
    counting_line = Column(String)

class BreadProduct(Base):
    __tablename__ = 'bread_products'

    product_id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    photos = Column(String)
    video = Column(String)

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

Camera.counting_results = relationship("CountingResult", back_populates="camera")
BreadProduct.counting_results = relationship("CountingResult", back_populates="product")
