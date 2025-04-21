
import asyncio
import struct
import random
from dbus_next.aio import MessageBus
from dbus_next import Variant, BusType
from dbus_next.service import ServiceInterface, method, dbus_property
from dbus_next.constants import PropertyAccess

SERVICE_UUID = '12345678-1234-5678-1234-56789abcdef0'

class Advertisement(ServiceInterface):
    def __init__(self, index):
        super().__init__('org.bluez.LEAdvertisement1')
        self.path = f'/org/bluez/example/advertisement{index}'
        self.latitude = 41.0
        self.longitude = 2.0
        self.altitude = 100
        self.update_payload()

    def update_payload(self):
        self.payload = struct.pack('<ffh', self.latitude, self.longitude, self.altitude)

    @dbus_property(PropertyAccess.READ)
    def Type(self) -> 's':
        return 'broadcast'

    @dbus_property(PropertyAccess.READ)
    def ServiceUUIDs(self) -> 'as':
        return [SERVICE_UUID]

    @dbus_property(PropertyAccess.READ)
    def ServiceData(self) -> 'a{sv}':
        return {SERVICE_UUID: Variant('ay', self.payload)}

    @dbus_property(PropertyAccess.READ)
    def IncludeTxPower(self) -> 'b':
        return False

    @method()
    def Release(self):
        print("Anuncio liberado")

async def register_advertisement(bus, adv):
    introspection = await bus.introspect('org.bluez', '/')
    obj = bus.get_proxy_object('org.bluez', '/', introspection)
    manager = obj.get_interface('org.freedesktop.DBus.ObjectManager')

    adapter_path = None
    objects = await manager.call_get_managed_objects()
    for path, interfaces in objects.items():
        if 'org.bluez.LEAdvertisingManager1' in interfaces:
            adapter_path = path
            break

    if not adapter_path:
        raise Exception("No se encontró adaptador BLE")

    adapter_introspect = await bus.introspect('org.bluez', adapter_path)
    adapter = bus.get_proxy_object('org.bluez', adapter_path, adapter_introspect)
    advertising_manager = adapter.get_interface('org.bluez.LEAdvertisingManager1')

    bus.export(adv.path, adv)
    await advertising_manager.call_register_advertisement(adv.path, {})

    print("🚀 Transmitiendo datos BLE... Ctrl+C para detener")

    try:
        while True:
            adv.latitude += random.uniform(-0.0001, 0.0001)
            adv.longitude += random.uniform(-0.0001, 0.0001)
            adv.altitude += random.choice([-1, 0, 1])
            adv.update_payload()
            print(f"📡 Lat: {adv.latitude:.5f} | Lon: {adv.longitude:.5f} | Alt: {adv.altitude}")
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        pass
    finally:
        await advertising_manager.call_unregister_advertisement(adv.path)
        print("🛑 Anuncio detenido")

async def main():
    bus = await MessageBus(bus_type=BusType.SYSTEM).connect()
    adv = Advertisement(index=0)
    await register_advertisement(bus, adv)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("🛑 Finalizado por el usuario")
