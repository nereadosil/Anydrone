
import asyncio
import struct
from dbus_next.aio import MessageBus
from dbus_next.service import ServiceInterface, method, dbus_property
from dbus_next.constants import PropertyAccess
from dbus_next import Variant, BusType

SERVICE_UUID = '12345678-1234-5678-1234-56789abcdef0'

class Advertisement(ServiceInterface):
    def __init__(self, index):
        super().__init__('org.bluez.LEAdvertisement1')
        self.path = f'/org/bluez/example/advertisement{index}'
        self.payload = b'\x01\x02\x03\x04'

    @dbus_property(PropertyAccess.READ)
    def Type(self):
        return Variant('s', 'broadcast')

    @dbus_property(PropertyAccess.READ)
    def ServiceUUIDs(self):
        return Variant('as', [SERVICE_UUID])

    @dbus_property(PropertyAccess.READ)
    def ServiceData(self):
        return Variant('a{sv}', {SERVICE_UUID: Variant('ay', self.payload)})

    @dbus_property(PropertyAccess.READ)
    def IncludeTxPower(self):
        return Variant('b', False)

    @method()
    def Release(self):
        print("Anuncio liberado")

async def main():
    bus = await MessageBus(bus_type=BusType.SYSTEM).connect()
    adv = Advertisement(index=0)

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

    print("🚀 Transmitiendo datos BLE sin anotaciones... Ctrl+C para detener")

    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("🛑 Interrumpido por el usuario")
        await advertising_manager.call_unregister_advertisement(adv.path)

asyncio.run(main())
