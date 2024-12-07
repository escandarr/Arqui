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

# Crear la tabla de casos si no existe
cursor.execute('''
    CREATE TABLE IF NOT EXISTS casos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        etiqueta TEXT NOT NULL,
        usuario TEXT NOT NULL,
        descripcion TEXT NOT NULL,
        abogado TEXT DEFAULT 'No asignado',
        id_usuario INTEGER NOT NULL,
        area_derecho TEXT DEFAULT 'General'
    )
''')
conn.commit()

try:
    # Enviar datos de inicio
    message = b'00010sinitsubcs'
    print('sending {!r}'.format(message))
    sock.sendall(message)
    sinit = 1

    while True:
        # Esperar la transacción
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

        comando = data[:12].decode()
        datos = data[12:].decode()

        if comando == "subcscliente":
            try:
                parts = datos.split('|')
                if len(parts) != 6:  # Añadimos el área del derecho
                    raise ValueError(f"Expected 6 parts but got {len(parts)}")

                etiqueta, usuario, descripcion, abogado, id_usuario, area_derecho = parts
                print(f"Processing SUBCSCLIENTE: {parts}")

                cursor.execute("INSERT INTO casos (etiqueta, usuario, descripcion, abogado, id_usuario, area_derecho) VALUES (?, ?, ?, ?, ?, ?)",
                               (etiqueta, usuario, descripcion, abogado, id_usuario, area_derecho))
                conn.commit()
                case_id = cursor.lastrowid
                respuesta = f"El caso {case_id} ha sido registrado exitosamente."
                print(f"Inserted: {respuesta}")
            except Exception as e:
                respuesta = f"Error procesando SUBCSCLIENTE: {e}"
                print(f"Error: {e}")

        elif comando == "subcsabogado":
            try:
                print("Processing SUBCSABOG: Solicitando lista de casos")
                cursor.execute("SELECT * FROM casos")
                casos = cursor.fetchall()
                respuesta = "\n".join([f"ID: {caso[0]}, Etiqueta: {caso[1]}, Usuario: {caso[2]}, Descripcion: {caso[3]}, Abogado: {caso[4]}, Área: {caso[6]}" for caso in casos])
            except Exception as e:
                respuesta = f"Error procesando SUBCSABOG: {e}"
                print(f"Error: {e}")

        else:
            respuesta = "Comando no reconocido."

        response_length = len(respuesta) + 5 + 12
        message = f"{response_length:05}".encode() + comando.encode() + respuesta.encode()
        print('sending {!r}'.format(message))
        sock.sendall(message)

finally:
    print('closing socket')
    conn.close()
    sock.close()
