import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.util.Arrays;
import java.util.UUID;
import tinyb.BluetoothDevice;
import tinyb.BluetoothManager;
import tinyb.BluetoothGattCharacteristic;

public class OpenDroneIdBLEReceiver {

    private static final UUID DRONE_ID_SERVICE_UUID = UUID.fromString("0000fd6f-0000-1000-8000-00805f9b34fb");
    private static final UUID DRONE_ID_CHARACTERISTIC_UUID = UUID.fromString("00002af0-0000-1000-8000-00805f9b34fb");

    public static void main(String[] args) {
        BluetoothManager manager = BluetoothManager.getBluetoothManager();
        BluetoothDevice droneDevice = findDroneDevice(manager);

        if (droneDevice != null) {
            BluetoothGattCharacteristic droneData = getDroneDataCharacteristic(droneDevice);
            if (droneData != null) {
                parseDroneData(droneData.readValue());
            }
        } else {
            System.out.println("No drone device found broadcasting BLE messages.");
        }
    }

    private static BluetoothDevice findDroneDevice(BluetoothManager manager) {
        for (BluetoothDevice device : manager.getDevices()) {
            if (device.getUUIDs().contains(DRONE_ID_SERVICE_UUID.toString())) {
                System.out.println("Drone device detected: " + device.getAddress());
                return device;
            }
        }
        return null;
    }

    private static BluetoothGattCharacteristic getDroneDataCharacteristic(BluetoothDevice device) {
        return device.getServices().stream()
                .filter(service -> service.getUUID().equals(DRONE_ID_SERVICE_UUID.toString()))
                .flatMap(service -> service.getCharacteristics().stream())
                .filter(characteristic -> characteristic.getUUID().equals(DRONE_ID_CHARACTERISTIC_UUID.toString()))
                .findFirst().orElse(null);
    }

    private static void parseDroneData(byte[] data) {
        if (data == null || data.length < 29) {
            System.out.println("Invalid or insufficient data received.");
            return;
        }

        ByteBuffer buffer = ByteBuffer.wrap(data).order(ByteOrder.LITTLE_ENDIAN);
        byte messageType = buffer.get();
        byte protocolVersion = buffer.get();
        byte[] uasId = new byte[20];
        buffer.get(uasId);
        float latitude = buffer.getFloat();
        float longitude = buffer.getFloat();
        short altitude = buffer.getShort();

        // Filtering: Only process valid Remote ID messages
        if (messageType == 0x02 && protocolVersion == 0x01) {
            System.out.println("Valid Remote ID Message Received:");
            System.out.println("UAS ID: " + new String(uasId).trim());
            System.out.println("Latitude: " + latitude);
            System.out.println("Longitude: " + longitude);
            System.out.println("Altitude: " + altitude + "m");
        } else {
            System.out.println("Received non-compliant or unknown message type.");
        }
    }
}
