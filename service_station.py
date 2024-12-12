from database import Session, ServiceOrder
from threading import Thread, Lock
from time import sleep
from datetime import datetime, timedelta

class ServiceStation:
    def __init__(self, workers):
        self.session = Session() # Создает сессию для работы с базой данных
        self.workers = workers # Устанавливает количество работников
        self.processing_thread = None # Устанавливает поток обработки заказов
        self.lock = Lock()  # Для синхронизации доступа к заказам

    def add_order(self, car_model, service_type, processing_time):
        #  Создает новый заказ
        new_order = ServiceOrder(car_model=car_model, service_type=service_type, processing_time=processing_time)
        self.session.add(new_order) # Добавляет заказ в сессию
        self.session.commit() # охраняет изменения в базе данных

    def update_order_status(self, order_id, status):
        order = self.session.query(ServiceOrder).filter_by(id=order_id).first() # Получает заказ по идентификатору
        if order:
            order.status = status # Обновляет статус заказа
            if status == 'В процессе':
                order.process_start_time = datetime.utcnow() # Устанавливает время начала обработки
            self.session.commit()

    def get_orders(self):
        return self.session.query(ServiceOrder).all() # Возвращает все заказы

    def clear_orders(self):
        self.session.query(ServiceOrder).delete() # Удаляет все заказы
        self.session.commit()

    def process_orders(self):
        while True:
            with self.lock:  # Блокируем доступ к заказам
                orders = self.get_orders() # Получает все заказы
                pending_orders = [order for order in orders if order.status == 'В ожидании'] # Получает заказы в статусе "В ожидании"
                in_progress_orders = [order for order in orders if order.status == 'В процессе'] # // Получает заказы в статусе "В процессе"

                # Обработка заказов в статусе "В процессе"
                for order in in_progress_orders:
                    if datetime.utcnow() - order.process_start_time >= timedelta(seconds=order.processing_time):
                        self.update_order_status(order.id, 'Завершено') # Обновляет статус заказа на "Завершено"

                # Обработка заказов в статусе "В ожидании"
                available_workers = self.workers - len(in_progress_orders) # Вычисляет количество доступных работников
                for _ in range(available_workers):
                    if pending_orders:
                        order = pending_orders.pop(0) # Получает первый заказ из списка ожидающих
                        self.update_order_status(order.id, 'В процессе') # Обновляет статус заказа на "В процессе"

            sleep(1)  # Проверка новых заказов

    def start_processing(self):
        if self.processing_thread is None or not self.processing_thread.is_alive():
            self.processing_thread = Thread(target=self.process_orders, daemon=True) # Создает поток для обработки заказов
            self.processing_thread.start() # Запускает поток
