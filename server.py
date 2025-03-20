import socket
import sqlite3

# Configuración del servidor
HOST = '127.0.0.1'  
PORT = 65432        

# Conectar a la base de datos SQLite
conn_db = sqlite3.connect("database/anydrone.db")  
cursor = conn_db.cursor()

# Crear el socket del servidor
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen()

print(f"Servidor escuchando en {HOST}:{PORT}")

while True:
    # Aceptar conexión de un cliente
    conn, addr = server_socket.accept()
    print(f"Conectado por {addr}")

    try:
        # Recibir datos del cliente
        data = conn.recv(1024).decode()
        print(f"Comando recibido: {data}")

        if data.lower().startswith("select") or data.lower().startswith("pragma"):
            # Consultas que devuelven resultados
            cursor.execute(data)
            resultados = cursor.fetchall()
            respuesta = "\n".join(str(row) for row in resultados) if resultados else "Sin resultados."
        
        else:
            # Para INSERT, UPDATE, DELETE
            cursor.execute(data)
            conn_db.commit()
            respuesta = "Operación ejecutada con éxito."

    except sqlite3.Error as e:
        respuesta = f"Error en la consulta: {str(e)}"

    # Enviar respuesta al cliente
    conn.sendall(respuesta.encode())

    # Cerrar conexión con el cliente (pero mantener el servidor activo)
    conn.close()

# Cerrar la base de datos cuando el servidor se detiene
conn_db.close()
server_socket.close()