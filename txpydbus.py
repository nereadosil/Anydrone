from pydbus import SystemBus
from gi.repository import GLib
import struct
import time
import threading
import random

LE_ADVERTISING_MANAGER_IFACE = 'org.bluez.LEAdvertisingManager1'
LE_ADVERTISEMENT_IFACE = 'org.bluez.LEAdvertisement1'
SERVICE_UUID = '0000fd6f-0000-1000-8000-00805f9b34fb'

class Advertisement:
    PATH_BASE = '/org/bluez/example/advertisement'

    def __init__(self, index):
        self.path = self.PATH_BASE + str(index)
        self.service_UUIDs = [SERVICE_UUID]
        self.service_data = {}
        self.local_name = 'RemoteIDSim'
        self.include_tx_power = True
        self.ad_type = 'broadcast'

    def get_properties(self):
        return {
            LE_ADVERTISEMENT_IFACE: {
                'Type': self.ad_type,
                'ServiceUUIDs': self.service_UUIDs,
                'ServiceData': {SERVICE_UUID: self.service_data[SERVICE_UUID]},
                'LocalName': self.local_name,
                'IncludeTxPower': self.include_tx_power
            }
        }

    def get_path(self):
        return self.path

    def Release(self):
        print("🔌 Anuncio liberado por BlueZ")

    _path = property(get_path)
    _interfaces = {LE_ADVERTISEMENT_IFACE: ['Release']}

def create_payload(lat, lon, alt):
    message_type = 0x02
    protocol_version = 0x01
    uas_id = b'DRONE1234567890123'
    return struct.pack('<BB20sffh', message_type, protocol_version, uas_id, lat, lon, alt)

class RemoteIDBeacon:
    def __init__(self):
        self.bus = SystemBus()
        self.adapter = self.bus.get('org.bluez', '/org/bluez/hci0')
        self.ad_manager = self.adapter[LE_ADVERTISING_MANAGER_IFACE]

        self.latitude = 41.40338
        self.longitude = 2.17403
        self.altitude = 120

        self.advert = Advertisement(0)
        self.update_service_data()

    def update_service_data(self):
        payload = create_payload(self.latitude, self.longitude, self.altitude)
        self.advert.service_data = {SERVICE_UUID: payload}

    def start(self):
        self.ad_manager.RegisterAdvertisement(self.advert._path, {})
        def update_loop():
            while True:
                self.latitude += random.uniform(-0.00001, 0.00001)
                self.longitude += random.uniform(-0.00001, 0.00001)
                self.altitude += random.choice([-1, 0, 1])
                self.update_service_data()
                print(f"📡 Emitiendo: lat={self.latitude:.6f}, lon={self.longitude:.6f}, alt={self.altitude} m")
                time.sleep(1)
        threading.Thread(target=update_loop, daemon=True).start()
        GLib.MainLoop().run()

if __name__ == '__main__':
    try:
        print("🚀 Transmisión BLE Remote ID iniciada con pydbus...")
        beacon = RemoteIDBeacon()
        beacon.start()
    except KeyboardInterrupt:
        print("🛑 Transmisión interrumpida por el usuario.")
