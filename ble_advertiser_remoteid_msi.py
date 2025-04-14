
#!/usr/bin/env python3
import dbus
import dbus.mainloop.glib
import dbus.service
from gi.repository import GLib
import struct
import random
import threading
import time

ADAPTER_PATH = "/org/bluez/hci0"
SERVICE_UUID = "0000fd6f-0000-1000-8000-00805f9b34fb"

class Advertisement(dbus.service.Object):
    PATH_BASE = "/org/bluez/example/advertisement"

    def __init__(self, bus, index):
        self.path = self.PATH_BASE + str(index)
        self.bus = bus
        self.service_uuid = SERVICE_UUID
        self.local_name = "RemoteIDSim"
        self.include_tx_power = True
        self.latitude = 41.40338
        self.longitude = 2.17403
        self.altitude = 120
        self.service_data = {}
        self.update_service_data()
        dbus.service.Object.__init__(self, bus, self.path)

    def get_path(self):
        return dbus.ObjectPath(self.path)

    def update_service_data(self):
        # Remote ID message simulation
        message_type = 0x02
        protocol_version = 0x01
        uas_id = b'DRONE1234567890123'
        payload = struct.pack('<BB20sffh', message_type, protocol_version, uas_id,
                              self.latitude, self.longitude, self.altitude)
        self.service_data = {self.service_uuid: dbus.ByteArray(payload)}

    @dbus.service.method("org.freedesktop.DBus.Properties", in_signature="ss", out_signature="v")
    def Get(self, interface, prop):
        if interface != "org.bluez.LEAdvertisement1":
            raise dbus.exceptions.DBusException("Invalid interface")
        if prop == "Type":
            return "broadcast"
        elif prop == "ServiceUUIDs":
            return [self.service_uuid]
        elif prop == "LocalName":
            return self.local_name
        elif prop == "IncludeTxPower":
            return self.include_tx_power
        elif prop == "ServiceData":
            return self.service_data
        else:
            raise dbus.exceptions.DBusException("Invalid property")

    @dbus.service.method("org.bluez.LEAdvertisement1", in_signature="", out_signature="")
    def Release(self):
        print("🔌 Anuncio liberado")

def register_advertisement(bus, advertisement):
    adapter = dbus.Interface(bus.get_object("org.bluez", ADAPTER_PATH),
                             "org.bluez.LEAdvertisingManager1")
    adapter.RegisterAdvertisement(advertisement.get_path(), {},
                                  reply_handler=lambda: print("📡 Anuncio BLE registrado"),
                                  error_handler=lambda e: print(f"❌ Error al registrar: {e}"))

def main():
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    bus = dbus.SystemBus()
    advertisement = Advertisement(bus, 0)
    register_advertisement(bus, advertisement)

    def update_loop():
        while True:
            advertisement.latitude += random.uniform(-0.00001, 0.00001)
            advertisement.longitude += random.uniform(-0.00001, 0.00001)
            advertisement.altitude += random.choice([-1, 0, 1])
            advertisement.update_service_data()
            print(f"📡 Emitiendo: lat={advertisement.latitude:.6f}, lon={advertisement.longitude:.6f}, alt={advertisement.altitude} m")
            time.sleep(1)

    threading.Thread(target=update_loop, daemon=True).start()
    GLib.MainLoop().run()

if __name__ == "__main__":
    main()
