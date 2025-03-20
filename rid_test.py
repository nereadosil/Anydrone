import asyncio
from bleak import BleakScanner
import struct

# UUID de servicio para Remote ID (según normativa ASTM F3411 y UNE-EN 4709-002:2023)
REMOTE_ID_UUID = "0000fd6f-0000-1000-8000-00805f9b34fb"

# Diccionario para almacenar información de los drones detectados
remote_id_data = {}

# Función para decodificar el mensaje Remote ID recibido
def decode_remote_id(data):
    if len(data) < 25:
        print("⚠️ Mensaje inválido (longitud incorrecta)")
        return
    
    # Extraer el encabezado del mensaje
    message_type = (data[0] >> 4) & 0x0F  # Primeros 4 bits -> Tipo de mensaje
    protocol_version = data[0] & 0x0F     # Últimos 4 bits -> Versión del protocolo
    
    print(f"📡 Mensaje Remote ID detectado!")
    print(f"🔹 Tipo de mensaje: {message_type}")
    print(f"🔹 Versión del protocolo: {protocol_version}")

    # Procesar cada tipo de mensaje según su estructura
    if message_type == 0x0:  # Basic ID Message
        uas_id = data[2:22].decode('utf-8', errors='ignore').strip('\x00')
        remote_id_data["uas_id"] = uas_id
        print("🆔 Basic ID Message:")
        print(f"   - UAS ID: {uas_id}")
    
    elif message_type == 0x1:  # Location/Vector Message
        status = (data[1] >> 4) & 0x0F
        direction = data[2]
        speed = data[3] * 0.25
        lat, lon, alt = struct.unpack('<iii', data[4:16])
        lat /= 10**7
        lon /= 10**7
        alt /= 1000
        remote_id_data.update({
            "lat": lat,
            "lon": lon,
            "alt": alt,
            "speed": speed,
            "direction": direction,
            "status": status
        })
        print("📍 Location/Vector Message:")
        print(f"   - Estado: {status}")
        print(f"   - Dirección: {direction}°")
        print(f"   - Velocidad: {speed} m/s")
        print(f"   - Latitud: {lat}")
        print(f"   - Longitud: {lon}")
        print(f"   - Altitud: {alt} m")
    
    elif message_type == 0x2:  # System Message
        emergency_status = data[1] & 0x0F
        print("🚨 System Message:")
        print(f"   - Estado de emergencia: {emergency_status}")
        remote_id_data["status"] = emergency_status
    
    print("-" * 50)

# Función para escanear dispositivos BLE y filtrar mensajes Remote ID
def filter_remote_id(device, advertisement_data):
    if REMOTE_ID_UUID in advertisement_data.service_uuids:
        print(f"📡 Dispositivo detectado: {device.address}")
        if advertisement_data.manufacturer_data:
            for key, value in advertisement_data.manufacturer_data.items():
                print(f"🔹 Datos HEX: {value.hex().upper()}")
                decode_remote_id(value)

async def scan_remote_id():
    print("🔍 Escaneando dispositivos BLE en busca de mensajes Remote ID...")
    scanner = BleakScanner(detection_callback=filter_remote_id)
    await scanner.start()
    await asyncio.sleep(30)  # Escaneará por 30 segundos
    await scanner.stop()
    
    # Mostrar la información consolidada del dron detectado
    print("\n📊 Información consolidada del dron:")
    for key, value in remote_id_data.items():
        print(f"{key}: {value}")

# Ejecutar el escaneo
asyncio.run(scan_remote_id())
