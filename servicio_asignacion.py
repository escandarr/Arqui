import socket
import sqlite3

# Crear un socket TCP/IP
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Conectar el socket al puerto donde el bus está escuchando
bus_address = ('localhost', 5000)
print('connecting to {} port {}'.format(*bus_address))
sock.connect(bus_address)

# Conectar a la base de datos SQLite
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Crear la tabla de especializaciones si no existe
cursor.execute('''
    CREATE TABLE IF NOT EXISTS especializaciones (
        abogado_id INTEGER NOT NULL,
        area_derecho TEXT NOT NULL,
        FOREIGN KEY(abogado_id) REFERENCES usuarios(id)
    )
''')
conn.commit()

try:
    # Enviar datos de inicio
    message = b'00010sinitasign'
    print('sending {!r}'.format(message))
    sock.sendall(message)
    sinit = 1

    while True:
        print("Waiting for transaction")
        amount_received = 0
        amount_expected = int(sock.recv(5))

        data = b""
        while amount_received < amount_expected:
            chunk = sock.recv(amount_expected - amount_received)
            amount_received += len(chunk)
            data += chunk

        if sinit == 1:
            sinit = 0
            print('Received sinit answer')
            continue

        comando = data[:10].decode()
        datos = data[10:].decode()

        if comando == "asignarcaso":
            try:
                consulta_id = int(datos)
                cursor.execute("SELECT area_derecho FROM casos WHERE id = ?", (consulta_id,))
                area = cursor.fetchone()
                if not area:
                    raise ValueError("Consulta no encontrada")

                cursor.execute('''
                    SELECT usuarios.id, usuarios.nombre 
                    FROM usuarios
                    JOIN especializaciones ON usuarios.id = especializaciones.abogado_id
                    WHERE especializaciones.area_derecho = ?
                    LIMIT 1
                ''', (area[0],))
                abogado = cursor.fetchone()
                if not abogado:
                    respuesta = "No hay abogados disponibles para esta área."
                else:
                    abogado_id, abogado_nombre = abogado
                    cursor.execute("UPDATE casos SET abogado = ? WHERE id = ?", (abogado_nombre, consulta_id))
                    conn.commit()
                    respuesta = f"El abogado {abogado_nombre} ha sido asignado al caso {consulta_id}."
            except Exception as e:
                respuesta = f"Error procesando asignación: {e}"

        response_length = len(respuesta) + 5 + 10
        message = f"{response_length:05}".encode() + comando.encode() + respuesta.encode()
        print('sending {!r}'.format(message))
        sock.sendall(message)

finally:
    print('closing socket')
    conn.close()
    sock.close()
