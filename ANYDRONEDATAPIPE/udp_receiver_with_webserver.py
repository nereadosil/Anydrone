import socket
import threading
import cherrypy
import time
import json
import requests  # <-- Importante para hacer POST

PORT = 5005
BUFFER_SIZE = 1024

device_data = {}

def udp_listener():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('', PORT))
    print("📡 Receptor Wi-Fi escuchando...")

    while True:
        try:
            data, addr = sock.recvfrom(BUFFER_SIZE)
            decoded = data.decode()
            print(f"📥 Recibido de {addr}: {decoded}")

            # Esperamos el mensaje en formato: ID,LAT,LON,ALT
            parts = decoded.split(",")
            if len(parts) == 4:
                drone_id, lat, lon, alt = parts
                device_data[addr[0]] = {
                    "uas_id": drone_id,
                    "latitude": float(lat),
                    "longitude": float(lon),
                    "altitude": float(alt),
                    "timestamp": time.time()
                }
        except Exception as e:
            print("❌ Error al procesar mensaje:", e)

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
        time.sleep(1)
        try:
            if not device_data:
                continue

            server_url = "http://127.0.0.1:5000/sync_drones"

            payload = {"drones": []}
            for addr, data in device_data.items():
                payload["drones"].append({
                    "drone_id": data.get("uas_id"),
                    "latitude": data.get("latitude"),
                    "longitude": data.get("longitude"),
                })

            response = requests.post(server_url, json=payload)
            if response.status_code == 200:
                print("✅ Datos sincronizados.")
            else:
                print(f"⚠️ Error del servidor: {response.status_code} - {response.text}")
        except Exception as e:
            print("❌ Error durante sincronización:", e)

def main():
    threading.Thread(target=udp_listener, daemon=True).start()
    threading.Thread(target=start_web_server, daemon=True).start()
    threading.Thread(target=sync_with_server, daemon=True).start()
    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()