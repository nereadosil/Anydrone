from bluezero import advertisement
import struct
import time
import random

SERVICE_UUID = '0000fd6f-0000-1000-8000-00805f9b34fb'

def create_payload(lat, lon, alt):
    message_type = 0x02
    protocol_version = 0x01
    uas_id = b'DRONE1234567890123'
    return struct.pack('<BB20sffh', message_type, protocol_version, uas_id, lat, lon, alt)

latitude = 41.40338
longitude = 2.17403
altitude = 120

adv = advertisement.Advertisement(1, 'broadcast')  # 💡 NO 'peripheral'
adv.service_UUIDs = [SERVICE_UUID]
adv.service_data = {
    SERVICE_UUID: create_payload(latitude, longitude, altitude)
}
adv.include_tx_power = False
adv.appearance = 0

def update_loop():
    global latitude, longitude, altitude
    while True:
        latitude += random.uniform(-0.00002, 0.00002)
        longitude += random.uniform(-0.00002, 0.00002)
        altitude += random.choice([-1, 0, 1])
        payload = create_payload(latitude, longitude, altitude)
        adv.service_data[SERVICE_UUID] = payload
        print("📡 Actualizando datos:", latitude, longitude, altitude)
        time.sleep(1)

try:
    print("🚀 Comenzando transmisión BLE (advertising)...")
    adv.start()
    update_loop()
except KeyboardInterrupt:
    print("🛑 Finalizado por el usuario")
    adv.stop()
