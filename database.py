from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()

class ServiceOrder(Base):
    __tablename__ = 'service_orders'
    id = Column(Integer, primary_key=True)
    car_model = Column(String, nullable=False)
    service_type = Column(String, nullable=False)
    status = Column(String, default='В ожидании')
    created_at = Column(DateTime, default=datetime.utcnow)
    process_start_time = Column(DateTime, nullable=True)
    processing_time = Column(Integer, default=5)  # Время выполнения заказа в секундах

engine = create_engine('sqlite:///service_orders.db', connect_args={"check_same_thread": False})
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
