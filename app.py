from flask import Flask, request, jsonify, render_template
from service_station import ServiceStation

app = Flask(__name__)
service_station = ServiceStation(workers=2)  # Начальное количество работников

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_order', methods=['POST'])
def add_order():
    data = request.json
    car_model = data.get('car_model')
    service_type = data.get('service_type')
    processing_time = data.get('processing_time', 5)  # Время выполнения заказа в секундах
    service_station.add_order(car_model, service_type, processing_time)
    return jsonify({'message': 'Заказ успешно добавлен'}), 201

@app.route('/get_orders', methods=['GET'])
def get_orders():
    orders = service_station.get_orders()
    orders_list = [{'id': order.id, 'car_model': order.car_model, 'service_type': order.service_type, 'status': order.status, 'created_at': order.created_at.isoformat()} for order in orders]
    return jsonify(orders_list), 200

@app.route('/clear_orders', methods=['POST'])
def clear_orders():
    service_station.clear_orders()
    return jsonify({'message': 'Список заказов очищен'}), 200

@app.route('/update_workers', methods=['POST'])
def update_workers():
    data = request.json
    workers = data.get('workers', 1)
    service_station.update_workers(workers)
    return jsonify({'message': f'Количество работников обновлено до {workers}'}), 200

if __name__ == '__main__':
    service_station.start_processing()
    app.run(debug=True)
