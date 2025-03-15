import socket

# Configuración del cliente
HOST = '127.0.0.1'
PORT = 65432

while True:
    # Pedir comando SQL al usuario
    sql_command = input("Introduce un comando SQL (o 'exit' para salir): ")

    if sql_command.lower() == 'exit':
        break

    # Crear el socket del cliente
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))  

    # Enviar comando SQL al servidor
    client_socket.sendall(sql_command.encode())

    # Recibir respuesta del servidor
    response = client_socket.recv(4096).decode()
    print(f"Respuesta del servidor:\n{response}")

    # Cerrar conexión
    client_socket.close()
