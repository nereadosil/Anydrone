from flask import Flask, render_template_string, abort
import firebase_admin
from firebase_admin import credentials, firestore
import time
import os
import json
from flask import redirect
from flask import make_response
import io
import csv
from datetime import datetime, timedelta



# 🔐 Inicializar Firebase
firebase_key_json = os.environ["FIREBASE_KEY"]
cred = credentials.Certificate(json.loads(firebase_key_json))
firebase_admin.initialize_app(cred)
db = firestore.client()

# 🚀 Iniciar app Flask
app = Flask(__name__)

# HTML embebido (puedes luego separarlo si lo deseas)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Sensor {{ sensor_id }}</title>
    <h2>🔍 Sensor: {{ sensor_id }}</h2>
    <!-- Botón de descarga -->
    <a href="/download/{{ sensor_id }}" class="btn btn-primary mb-3" target="_blank">
        📥 Descargar datos (últimos 3 días)
    </a>
    <meta http-equiv="refresh" content="3">
    <style>
        {% raw %}
        body {
            font-family: Arial, sans-serif;
            background-color: #f4f6f8;
            padding: 2rem;
        }
        .card {
            background: white;
            padding: 2rem;
            border-radius: 1rem;
            box-shadow: 0 0 12px rgba(0,0,0,0.1);
            max-width: 400px;
            margin: auto;
        }
        h2 {
            margin-bottom: 1rem;
        }
        .metric {
            font-size: 1.2rem;
            margin-bottom: 0.5rem;
        }
        {% endraw %}
    </style>
</head>
<body>
    <div class="card">
        <h2>🔍 Sensor: {{ sensor_id }}</h2>
        <div class="metric">🌡 <b>Temperatura:</b> {{ data.temperature }} °C</div>
        <div class="metric">💧 <b>Humedad:</b> {{ data.humidity }} %</div>
        <div class="metric">🔽 <b>Presión:</b> {{ data.pressure }} hPa</div>
        <div class="metric">🧪 <b>Gas:</b> {{ data.gas }} Ω</div>
        <div class="metric"><small>⏱ {{ timestamp }}</small></div>
    </div>
</body>
</html>
"""
@app.route('/download/<sensor_id>')
def download_sensor_data(sensor_id):
    three_days_ago = time.time() - (3 * 24 * 60 * 60)

    # Consultar Firestore por las lecturas del sensor en los últimos 3 días
    query = db.collection("temperature_logs")\
              .where("sensor_id", "==", sensor_id)\
              .where("timestamp", ">=", three_days_ago)\
              .order_by("timestamp")\
              .stream()

    entries = [doc.to_dict() for doc in query]

    if not entries:
        abort(404, description="No se encontraron datos recientes para este sensor.")

    # Crear CSV en memoria
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["timestamp", "sensor_id", "temperature", "humidity", "pressure", "gas"])

    for entry in entries:
        writer.writerow([
            datetime.fromtimestamp(entry["timestamp"]).isoformat(),
            entry["sensor_id"],
            entry["temperature"],
            entry["humidity"],
            entry["pressure"],
            entry["gas"]
        ])

    # Enviar como descarga
    response = make_response(output.getvalue())
    response.headers["Content-Disposition"] = f"attachment; filename={sensor_id}_last_3_days.csv"
    response.headers["Content-type"] = "text/csv"
    return response

@app.route('/stream/<sensor_id>')
def stream(sensor_id):
    doc = db.collection("temperature").document(sensor_id).get()
    if not doc.exists:
        abort(404, description=f"Sensor {sensor_id} no encontrado.")
    
    data = doc.to_dict()
    ts = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(data.get("timestamp", 0)))
    
    return render_template_string(
        HTML_TEMPLATE,
        sensor_id=sensor_id,
        data=data,
        timestamp=ts
    )

# 🔧 Página raíz opcional
@app.route("/")
def index():
    return redirect("/stream/TEMP_RPI_BME680")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8081, debug=True)
