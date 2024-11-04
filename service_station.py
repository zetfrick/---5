from database import Session, ServiceOrder
from threading import Thread
from time import sleep
from datetime import datetime, timedelta

class ServiceStation:
    def __init__(self, workers=1):
        self.session = Session()
        self.workers = workers
        self.processing_thread = None

    def add_order(self, car_model, service_type, processing_time):
        new_order = ServiceOrder(car_model=car_model, service_type=service_type, processing_time=processing_time)
        self.session.add(new_order)
        self.session.commit()

    def update_order_status(self, order_id, status):
        order = self.session.query(ServiceOrder).filter_by(id=order_id).first()
        if order:
            order.status = status
            if status == 'В процессе':
                order.process_start_time = datetime.utcnow()
            self.session.commit()

    def get_orders(self):
        return self.session.query(ServiceOrder).all()

    def clear_orders(self):
        self.session.query(ServiceOrder).delete()
        self.session.commit()

    def process_orders(self):
        while True:
            orders = self.get_orders()
            pending_orders = [order for order in orders if order.status == 'В ожидании']
            in_progress_orders = [order for order in orders if order.status == 'В процессе']

            # Обработка заказов в статусе "В процессе"
            for order in in_progress_orders:
                if datetime.utcnow() - order.process_start_time >= timedelta(seconds=order.processing_time):
                    self.update_order_status(order.id, 'Завершено')

            # Обработка заказов в статусе "В ожидании"
            available_workers = self.workers - len(in_progress_orders)
            for _ in range(available_workers):
                if pending_orders:
                    order = pending_orders.pop(0)
                    self.update_order_status(order.id, 'В процессе')

            sleep(1)  # Проверка новых заказов каждые 1 секунду

    def start_processing(self):
        if self.processing_thread is None or not self.processing_thread.is_alive():
            self.processing_thread = Thread(target=self.process_orders, daemon=True)
            self.processing_thread.start()

    def update_workers(self, workers):
        self.workers = workers
        if self.processing_thread is not None and self.processing_thread.is_alive():
            self.processing_thread.join()  # Ожидание завершения текущего потока
        self.start_processing()  # Перезапуск обработки заказов с новым количеством работников
