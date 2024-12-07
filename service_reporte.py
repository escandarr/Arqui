import socket
import sqlite3
import json

# Crear un socket TCP/IP
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Conectar el socket al puerto donde el bus está escuchando
bus_address = ('localhost', 5000)
print('connecting to {} port {}'.format(*bus_address))
sock.connect(bus_address)

# Conectar a la base de datos SQLite
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Crear la tabla de reportes si no existe
cursor.execute('''
    CREATE TABLE IF NOT EXISTS reportes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        consulta_id INTEGER NOT NULL,
        progreso TEXT NOT NULL,
        fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(consulta_id) REFERENCES casos(id)
    )
''')
conn.commit()

try:
    # Enviar datos de inicialización al bus
    message = b'00010sinitrepor'
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

        comando = data[:5].decode()  # Decodificar comando (e.g., "repor" o "histreportes")
        datos = data[5:].decode()   # Decodificar datos adicionales

        print(f"Comando recibido: {comando}")
        print(f"Datos recibidos: {datos}")

        if comando == "repor":  # Generar Reporte
            try:
                consulta_id = int(datos)
                cursor.execute("SELECT * FROM casos WHERE id = ?", (consulta_id,))
                caso = cursor.fetchone()
                if not caso:
                    respuesta = "Consulta no encontrada."
                else:
                    reporte = {
                        "ID Caso": caso[0],
                        "Etiqueta": caso[1],
                        "Usuario": caso[2],
                        "Descripción": caso[3],
                        "Abogado": caso[4],
                        "Área del Derecho": caso[6],
                        "Progreso": "En progreso"
                    }

                    # Insertar reporte en la tabla de reportes
                    cursor.execute("INSERT INTO reportes (consulta_id, progreso) VALUES (?, ?)", (consulta_id, reporte["Progreso"]))
                    conn.commit()

                    respuesta = json.dumps(reporte)
                    print(f"Reporte generado: {respuesta}")
            except Exception as e:
                respuesta = f"Error al generar reporte: {e}"
                print(f"Error: {e}")

        elif comando == "histreportes":  # Historial de Reportes
            try:
                consulta_id = int(datos)
                cursor.execute("SELECT id, progreso, fecha FROM reportes WHERE consulta_id = ?", (consulta_id,))
                reportes = cursor.fetchall()
                if not reportes:
                    respuesta = "No hay reportes disponibles para esta consulta."
                else:
                    historial = [{"ID Reporte": rep[0], "Progreso": rep[1], "Fecha": rep[2]} for rep in reportes]
                    respuesta = json.dumps(historial)
                    print(f"Historial generado: {respuesta}")
            except Exception as e:
                respuesta = f"Error al obtener historial de reportes: {e}"
                print(f"Error: {e}")

        else:  # Comando desconocido
            respuesta = "Comando no reconocido."
            print("Comando desconocido recibido.")

        # Enviar respuesta al bus
        response_length = len(respuesta) + len(comando)
        message = f"{response_length:05}{comando}{respuesta}".encode()
        print('Enviando respuesta: {!r}'.format(message))
        sock.sendall(message)

finally:
    print('Cerrando conexión...')
    conn.close()
    sock.close()
