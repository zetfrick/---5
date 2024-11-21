from flask import Flask, request, jsonify, render_template
from service_station import ServiceStation
import os

app = Flask(__name__)

# Функция для получения количества работников из файла config.txt
def get_workers_count():
    try:
        with open("config.txt", "r") as f:
            content = f.read().strip()
            # Если файл пустой, возвращаем 0 (или другое значение по умолчанию)
            if not content:
                return 0
            return int(content)
    except FileNotFoundError:
        # Если файл не найден, возвращаем значение по умолчанию
        return 0
    except ValueError:
        # Если в файле содержится неправильное значение, возвращаем значение по умолчанию
        return 0

# Функция для записи количества работников в файл config.txt
def set_workers_count(workers):
    with open("config.txt", "w") as f:
        f.write(str(workers))

# Проверка наличия сохраненного числа работников в файле
workers_count = get_workers_count()

# Инициализация service_station, если количество работников задано
service_station = None
if workers_count > 0:
    service_station = ServiceStation(workers=workers_count)
    service_station.start_processing()  # Начинаем обработку заказов

@app.route('/')
def index():
    if workers_count <= 0:
        # Если количество работников не задано, показываем форму для ввода
        return render_template('set_workers.html')
    else:
        # Если количество работников задано, отображаем основную страницу
        return render_template('index.html')

# Маршрут для установки количества работников
@app.route('/set_workers', methods=['POST'])
def set_workers():
    workers = int(request.form['workers'])  # Получаем количество работников из формы
    
    # Записываем количество работников в файл config.txt
    set_workers_count(workers)
    
    global workers_count, service_station
    workers_count = workers  # Обновляем переменную в приложении
    
    # Создаем новый объект с обновленным количеством работников
    service_station = ServiceStation(workers=workers_count)
    service_station.start_processing()  # Запускаем обработку заказов
    
    return jsonify({'message': f'Количество работников обновлено до {workers_count}'}), 200


# Основной маршрут для добавления заказов
@app.route('/add_order', methods=['POST'])
def add_order():
    if service_station is None:
        return jsonify({'error': 'Станция обслуживания не настроена!'}), 400
    
    data = request.json
    car_model = data.get('car_model')
    service_type = data.get('service_type')
    processing_time = data.get('processing_time', 5)  # Время выполнения заказа в секундах
    service_station.add_order(car_model, service_type, processing_time)
    return jsonify({'message': 'Заказ успешно добавлен'}), 201

# Получение списка всех заказов
@app.route('/get_orders', methods=['GET'])
def get_orders():
    if service_station is None:
        return jsonify({'error': 'Станция обслуживания не настроена!'}), 400
    
    orders = service_station.get_orders()
    orders_list = [{'id': order.id, 'car_model': order.car_model, 'service_type': order.service_type, 'status': order.status, 'created_at': order.created_at.isoformat()} for order in orders]
    return jsonify(orders_list), 200

# Очистка всех заказов
@app.route('/clear_orders', methods=['POST'])
def clear_orders():
    if service_station is None:
        return jsonify({'error': 'Станция обслуживания не настроена!'}), 400
    
    service_station.clear_orders()
    return jsonify({'message': 'Список заказов очищен'}), 200

# Обновление количества работников
@app.route('/update_workers', methods=['POST'])
def update_workers():
    if service_station is None:
        return jsonify({'error': 'Станция обслуживания не настроена!'}), 400
    
    data = request.json
    workers = data.get('workers', 1)
    service_station.update_workers(workers)
    return jsonify({'message': f'Количество работников обновлено до {workers}'}), 200

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
