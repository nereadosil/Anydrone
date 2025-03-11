import socket

# Configuración del cliente
HOST= '127.0.0.1'   #Dirección IP del server
PORT= 65432         #Puerto del server

#Crear el socket del cliente

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))     #Conectar al server

#Enviar mensaje al server

client_socket.sendall("Hola, servidor!".encode())

#Recibir respuesta del server

response = client_socket.recv(1024).decode()
print(f"Servidor responde: {response}")

#Cerrar conexión

client_socket.close()
