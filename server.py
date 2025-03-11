import socket

# Configuración del servidor
HOST = '127.0.0.1'  # Dirección local (localhost)
PORT = 65432        # Puerto de comunicación

# Crear el socket del servidor
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))  # Asignar host y puerto
server_socket.listen()  # Escuchar conexiones

print(f"Servidor escuchando en {HOST}:{PORT}")

# Esperar conexión de un cliente
conn, addr = server_socket.accept()
print(f"Conectado por {addr}")

# Recibir datos del cliente
data = conn.recv(1024).decode()
print(f"Cliente dice: {data}")

# Enviar respuesta al cliente
conn.sendall("Mensaje recibido".encode())

# Cerrar la conexión
conn.close()
server_socket.close()