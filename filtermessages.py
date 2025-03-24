import asyncio
from bleak import BleakScanner
import struct

# Define known Direct Remote ID Message Types
DIRECT_REMOTE_ID_MSG_TYPES = {
    0x00: "Basic ID Message",
    0x01: "Location/Vector Message",
    0x02: "Authentication Message",
    0x03: "Self-ID Message",
    0x04: "System Message",
    0x05: "Operator ID Message",
    0x0F: "Message Pack"
}

async def scan_ble():
    print("🔍 Scanning BLE devices for Direct Remote ID messages...")
    devices = await BleakScanner.discover()
    
    for device in devices:
        print(f"\n📡 Device: {device.address} - {device.name}")
        
        # Check for manufacturer data
        if device.metadata and "manufacturer_data" in device.metadata:
            for key, value in device.metadata["manufacturer_data"].items():
                print(f"  - Manufacturer ID: {hex(key)}")
                print(f"  - Raw Data: {value.hex()}")
                
                # Try to parse the Direct Remote ID message
                if len(value) >= 25:  # Ensure minimum message length
                    msg_type = value[0] & 0x0F  # First 4 bits indicate the type
                    protocol_version = (value[0] >> 4) & 0x0F
                    
                    msg_name = DIRECT_REMOTE_ID_MSG_TYPES.get(msg_type, "Unknown Message Type")
                    print(f"  ➤ Detected Direct Remote ID Message: {msg_name}")
                    print(f"  ➤ Protocol Version: {protocol_version}")
                    
                    if msg_type == 0x00:  # Basic ID Message
                        type= value[1].decode
                        uas_id = value[2:22].decode(errors='ignore').strip('\x00')
                        print(f"    ➤ UAS ID: {uas_id}")
                        print(f"    ➤ ID and UA type: {type}")
                    elif msg_type == 0x01:  # Location/Vector Message
                        latitude, longitude = struct.unpack('<ii', value[5:13])
                        print(f"    ➤ Latitude: {latitude / 1e7}, Longitude: {longitude / 1e7}")
                    elif msg_type == 0x02:  # Authentication Message
                        auth_type = value[1]
                        print(f"    ➤ Authentication Type: {auth_type}")
                    elif msg_type == 0x03:  # Self-ID Message
                        description = value[1:].decode(errors='ignore').strip('\x00')
                        print(f"    ➤ Self-ID Description: {description}")
                    elif msg_type == 0x04:  # System Message
                        print("    ➤ System Message Detected")
                    elif msg_type == 0x05:  # Operator ID Message
                        operator_id = value[1:].decode(errors='ignore').strip('\x00')
                        print(f"    ➤ Operator ID: {operator_id}")
                    elif msg_type == 0x0F:  # Message Pack
                        print("    ➤ Message Pack Detected (contains multiple messages)")
                else:
                    print("  ⚠️ Data too short to be a valid Direct Remote ID message")

asyncio.run(scan_ble())
