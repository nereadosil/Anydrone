import asyncio
from bleak import BleakScanner, BleakClient
import struct
import cherrypy
import threading
import sys
import termios
import tty
DRONE_ID_SERVICE_UUID = "0000fd6f-0000-1000-8000-00805f9b34fb"
DRONE_ID_CHAR_UUID = "00002af0-0000-1000-8000-00805f9b34fb"

latest_data= {}


def parse_remoteid_data(data):
    try:
        nmss,message_type, protocol_version, uas_id, lat, lon, altitude = struct.unpack("<BB20sffh", data)
        uas_id = uas_id.decode('utf-8').strip('\x00')
        return {

            "message_type": message_type,
            "protocol_version": protocol_version,
            "uas_id": uas_id,
            "latitude": lat,
            "longitude": lon,
            "altitude": altitude

        }
    except struct.error as e:
        print("error al desempaquetar datos:", e)
        return None

async def scan_and_receive():
    print("iniciando escaneo BLE usando bleak...")
    devices = await BleakScanner.discover(timeout=50)
    


    for d in devices:

        if(d.address== 'DC:A6:32:8D:C6:4B'):
            print(f"dispositivo encontrado: {d.address} - {d.name}")

            # Start web server in a thread
            web_thread = threading.Thread(target=start_web_server)
            web_thread.daemon = True
            web_thread.start()




            print("All services stopped. Goodbye!")
            try:
                async with BleakClient(d.address) as client:
                    services = client.services
                    if DRONE_ID_SERVICE_UUID.lower() in [s.uuid.lower() for s in services]:
                        print(f"✅ conectado a dispositivo con Remote ID: {d.address}")

                        while True:
                            data = await client.read_gatt_char(DRONE_ID_CHAR_UUID)
                            parsed = parse_remoteid_data(data)
                            if parsed:
                                global latest_data
                                latest_data = parsed
                                print("📡 datos recibidos:", parsed)
                            await asyncio.sleep(1)
                            
                              

                            
            except Exception as e:
                print("⚠️ error conectando o recibiendo datos:", e)


class RemoteIDWebService:

    counter=0
    
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def index(self):
        
        
    
        RemoteIDWebService.counter += 1
        print(f"🌐 Web request #{RemoteIDWebService.counter}")
        return latest_data
    


def start_web_server():
    cherrypy.quickstart(RemoteIDWebService(), '/', {
    '/': {
        'tools.response_headers.on': True,
        'tools.response_headers.headers': [('Content-Type', 'application/json')],
        }
    })

def wait_for_keypress(shutdown_key='q'):
    """Waits for a keypress and shuts everything down."""
    print(f"Press '{shutdown_key}' to stop the receiver and exit...")

    # Configure stdin to read one character
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        while True:
            ch = sys.stdin.read(1)
            if ch.lower() == shutdown_key:
                print(f"\n'{shutdown_key}' pressed. Shutting down...")
                cherrypy.engine.exit()  # This stops the CherryPy server
                break
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)




    



'''

# Start web server in a separate thread
web_thread = threading.Thread(target=start_web_server)
web_thread.start()

'''


asyncio.run(scan_and_receive())
