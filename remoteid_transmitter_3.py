from bluezero import peripheral
import struct
import time

adapter_address = 'DC:A6:32:8D:C6:4B'  # sustituye con tu dirección MAC de hci0

SERVICE_UUID = '0000fd6f-0000-1000-8000-00805f9b34fb'
CHAR_UUID = '00002af0-0000-1000-8000-00805f9b34fb'

def create_payload():
    message_type = 0x02
    protocol_version = 0x01
    uas_id = b'DRONE1234567890123'
    latitude = 41.40338
    longitude = 2.17403
    altitude = 120
    
    return struct.pack('<BB20sffh', message_type, protocol_version, uas_id, latitude, longitude, altitude)

# crea periférico BLE
remoteid = peripheral.Peripheral(adapter_address=adapter_address,
                                 local_name='RemoteIDDrone')

remoteid.add_service(srv_id=1, uuid=SERVICE_UUID, primary=True)

remoteid.add_characteristic(srv_id=1,
                            chr_id=1,
                            uuid=CHAR_UUID,
                            flags=['read', 'notify'],
                            notifying=True,
                            value=create_payload())

remoteid.pairable = True
remoteid.connectable = True

try:
    print('🚀 emitiendo Remote ID desde Raspberry...')
    remoteid.publish()
    while True:
        payload = create_payload()
        remoteid.update_characteristic_value(srv_id=1, chr_id=1, value=payload)
        print('📡 payload actualizado y transmitido')
        time.sleep(1)

except KeyboardInterrupt:
    print('🛑 transmisión interrumpida por el usuario')
