from flask import Flask, render_template_string, jsonify

app = Flask(__name__)

TEMPLATE = """
<!doctype html>
<html lang="ru">
<head>
    <meta charset="utf-8">
    <title>Устройства умного дома</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f4f4f9;
            margin: 0;
            padding: 20px;
        }
        h1 {
            color: #333;
            text-align: center;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
        }
        .device-list, .sensor-data {
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            padding: 20px;
            margin-bottom: 20px;
        }
        ul {
            list-style: none;
            padding: 0;
        }
        li {
            padding: 10px;
            border-bottom: 1px solid #eee;
        }
        li:last-child {
            border-bottom: none;
        }
        .sensor-value {
            font-weight: bold;
            color: #007bff;
        }
        .device-section {
            margin-bottom: 15px;
        }
        .device-section h3 {
            margin: 0 0 10px 0;
            color: #555;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Устройства умного дома</h1>
        <div class="device-list">
            <h2>Подключенные устройства</h2>
            <ul id="devices">
                {% for device in devices %}
                    <li>{{ device }}</li>
                {% endfor %}
            </ul>
        </div>
        <div class="sensor-data">
            <h2>Данные с датчиков</h2>
            <div id="sensor-data">
                <!-- Данные будут обновляться через JavaScript -->
            </div>
        </div>
    </div>
    <script>
        const keyNames = {
            "temperature": "Температура",
            "cpu_usage": "Загрузка CPU",
            "memory_usage": "Использование памяти",
            "status": "Статус"
        };

        function updateSensorData() {
            fetch('/data')
                .then(response => response.json())
                .then(data => {
                    const sensorContainer = document.getElementById('sensor-data');
                    sensorContainer.innerHTML = ''; // Очищаем контейнер
                    if (data.sensor_data) {
                        for (const [device, metrics] of Object.entries(data.sensor_data)) {
                            let html = `<div class="device-section"><h3>${device}</h3><ul>`;
                            for (const [key, value] of Object.entries(metrics)) {
                                let displayValue = value;
                                if (key === 'temperature') displayValue += '°C';
                                if (key === 'cpu_usage' || key === 'memory_usage') displayValue += '%';
                                html += `<li>${keyNames[key] || key}: <span class="sensor-value">${displayValue}</span></li>`;
                            }
                            html += '</ul></div>';
                            sensorContainer.innerHTML += html;
                        }
                    }
                    if (sensorContainer.innerHTML === '') {
                        sensorContainer.innerHTML = '<p>Нет данных</p>';
                    }
                })
                .catch(error => console.error('Ошибка:', error));
        }

        // Обновляем данные каждые 5 секунд
        setInterval(updateSensorData, 5000);
        // Вызываем сразу при загрузке
        updateSensorData();
    </script>
</body>
</html>
"""

@app.route("/")
def index():
    state = app.config.get('state')
    devices = state.get_data('devices') or [] if state else []
    return render_template_string(TEMPLATE, devices=devices)

@app.route("/data")
def get_data():
    state = app.config.get('state')
    if state:
        return jsonify({"sensor_data": state.get_data("sensor_data") or {}})
    return jsonify({"sensor_data": {}})