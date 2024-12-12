from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base() # Создает базовый класс

# Объявляет модель
class ServiceOrder(Base):
    __tablename__ = 'service_orders' # Устанавливает имя таблицы
    # Устанавливает поля
    id = Column(Integer, primary_key=True)
    car_model = Column(String, nullable=False)
    service_type = Column(String, nullable=False)
    status = Column(String, default='В ожидании')
    created_at = Column(DateTime, default=datetime.utcnow)
    process_start_time = Column(DateTime, nullable=True)
    processing_time = Column(Integer, default=5)  # Время выполнения заказа в секундах

# Создает движок
engine = create_engine('sqlite:///service_orders.db', connect_args={"check_same_thread": False})
# Создает таблицы
Base.metadata.create_all(engine)
# Создает сессию для работы с базой данных
Session = sessionmaker(bind=engine)
