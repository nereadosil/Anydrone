import asyncio
from bleak import BleakScanner

async def scan_ble():
    print("🔍 Escaneando dispositivos BLE...")
    devices = await BleakScanner.discover()
    for device in devices:
        print(f"\n📡 Dispositivo: {device.address} - {device.name}")
        
        # Mostrar datos de servicio si están disponibles
        if device.metadata and "uuids" in device.metadata:
            print("🔹 UUIDs de servicio detectados:")
            for uuid in device.metadata["uuids"]:
                print(f"  - {uuid}")
        
        # Mostrar manufacturer data si está disponible
        if device.metadata and "manufacturer_data" in device.metadata:
            print("🔹 Datos de fabricante detectados:")
            for key, value in device.metadata["manufacturer_data"].items():
                print(f"  - ID Fabricante: {hex(key)}")
                print(f"  - Datos HEX: {value.hex()}")
    
asyncio.run(scan_ble())