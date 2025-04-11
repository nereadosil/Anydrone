import asyncio
from bleak import BleakScanner
import struct
import cherrypy
import threading
import time
import requests

DRONE_ID_SERVICE_UUID = "0000fd6f-0000-1000-8000-00805f9b34fb"

device_data = {}

def parse_remoteid_data(data: bytes):
    try:
        message_type, protocol_version, uas_id, lat, lon, altitude = struct.unpack("<BB20sffh", data)
        uas_id = uas_id.decode('utf-8').strip('\x00')
        return {
            "message_type": message_type,
            "protocol_version": protocol_version,
            "uas_id": uas_id,
            "latitude": lat,
            "longitude": lon,
            "altitude": altitude
        }
    except Exception as e:
        print("❌ Error al parsear advertisement:", e)
        return None

def detection_callback(device, advertisement_data):
    service_data = advertisement_data.service_data
    if DRONE_ID_SERVICE_UUID.lower() in service_data:
        raw = service_data[DRONE_ID_SERVICE_UUID.lower()]
        parsed = parse_remoteid_data(raw)
        if parsed:
            device_data[device.address] = parsed
            print(f"📡 Datos recibidos de {device.address}:", parsed)

async def scan_loop():
    scanner = BleakScanner()
    scanner.register_detection_callback(detection_callback)
    await scanner.start()
    print("🔎 Escuchando anuncios BLE sin conexión...")

    while True:
        await asyncio.sleep(1)

class RemoteIDWebService:
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def index(self):
        return device_data

def start_web_server():
    cherrypy.quickstart(RemoteIDWebService(), '/', {
        '/': {
            'tools.response_headers.on': True,
            'tools.response_headers.headers': [('Content-Type', 'application/json')],
        }
    })

def sync_with_server():
    while True:
        time.sleep(10)
        try:
            if not device_data:
                continue

            server_url = "http://127.0.0.1:5000/sync_drones"

            payload = {"drones": []}
            for addr, data in device_data.items():
                payload["drones"].append({
                    "drone_id": data.get("uas_id"),
                    "model": "Unknown",
                    "manufacturer": "Unknown",
                    "camera_quality": "Unknown",
                    "max_load": 0,
                    "flight_time": 0,
                    "latitude": data.get("latitude"),
                    "longitude": data.get("longitude"),
                    "owner_id": "local_user"
                })

            response = requests.post(server_url, json=payload)
            if response.status_code == 200:
                print("✅ Datos sincronizados.")
            else:
                print(f"⚠️ Error del servidor: {response.status_code} - {response.text}")
        except Exception as e:
            print("❌ Error durante sincronización:", e)

def main():
    threading.Thread(target=start_web_server, daemon=True).start()
    threading.Thread(target=sync_with_server, daemon=True).start()
    asyncio.run(scan_loop())

if __name__ == "__main__":
    main()
