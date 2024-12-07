import socket
import sqlite3

# Crear un socket TCP/IP
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Conectar el socket al puerto donde el bus está escuchando
bus_address = ('localhost', 5000)
print('Conectando a {} puerto {}'.format(*bus_address))
sock.connect(bus_address)

# Conectar a la base de datos SQLite
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Crear la tabla de abogados si no existe
cursor.execute('''
    CREATE TABLE IF NOT EXISTS abogados (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        especialidad TEXT NOT NULL
    )
''')
conn.commit()

try:
    # Enviar datos de inicialización al bus
    message = b'00010sinitabogs'
    print('Enviando {!r}'.format(message))
    sock.sendall(message)

    while True:
        # Esperar la transacción
        print("Esperando transacción")
        amount_received = 0
        amount_expected = int(sock.recv(5))

        data = b""
        while amount_received < amount_expected:
            chunk = sock.recv(amount_expected - amount_received)
            data += chunk
            amount_received += len(chunk)

        comando = data[:10].decode()  # Decodificar el comando recibido
        datos = data[10:].decode()  # Decodificar los datos asociados al comando

        if comando == "sinitOKabo":
            print("Servicio inicializado correctamente en el bus.")
            continue

        elif comando == "listabogs":
            try:
                cursor.execute("SELECT id, nombre, especialidad FROM abogados")
                abogados = cursor.fetchall()
                if abogados:
                    respuesta = "\n".join([f"ID: {abogado[0]}, Nombre: {abogado[1]}, Especialidad: {abogado[2]}" for abogado in abogados])
                else:
                    respuesta = "No hay abogados registrados."
            except Exception as e:
                respuesta = f"Error listando abogados: {e}"
            response_length = len(respuesta) + 10
            message = f"{response_length:05}".encode() + b"listabogs" + respuesta.encode()
            sock.sendall(message)

        else:
            print("Comando no reconocido:", comando)

finally:
    print('Cerrando el socket')
    conn.close()
    sock.close()
