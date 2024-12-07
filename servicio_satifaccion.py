import socket
import sys
import sqlite3
import json

BUS_HOST = 'localhost'
BUS_PORT = 5000

# Conexión al bus
print('[SERVICIO] Conectando al bus...')
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((BUS_HOST, BUS_PORT))
print('[SERVICIO] Conectado al bus.')

# Conexión a la base de datos
conn = sqlite3.connect('database.db')
cursor = conn.cursor()
print('[SERVICIO] Conectado a la BD.')

# Crear la tabla evaluaciones si no existe
cursor.execute('''
    CREATE TABLE IF NOT EXISTS evaluaciones (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        consulta_id INTEGER NOT NULL,
        calificacion INTEGER NOT NULL,
        comentarios TEXT NOT NULL,
        fecha_evaluacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')
conn.commit()

try:
    # Registrar el servicio ante el bus
    init_message = b'00010sinitrpts1'
    print('[SERVICIO] Enviando mensaje de inicio:', init_message)
    sock.sendall(init_message)
    sinit = True

    while True:
        print('[SERVICIO] Esperando tamaño del siguiente mensaje...')
        size_data = sock.recv(5)
        if not size_data:
            print('[SERVICIO] No se recibió tamaño, cerrando...')
            break

        amount_expected = int(size_data)
        data = b""
        amount_received = 0
        while amount_received < amount_expected:
            chunk = sock.recv(amount_expected - amount_received)
            if not chunk:
                print('[SERVICIO] No se recibió más data. Cerrando...')
                break
            amount_received += len(chunk)
            data += chunk

        if sinit:
            # Primer mensaje es la respuesta a sinit
            sinit = False
            print('[SERVICIO] Respuesta a sinit recibida. Listo para procesar.')
            continue

        # Verificar si el mensaje es para este servicio
        if data[:5].decode() == 'rpts1':
            # Mensaje para este servicio
            comando = data[:10].decode()  # ej: rpts1repsa
            contenido = data[10:].decode()
            print('[SERVICIO] Comando recibido:', comando)
            print('[SERVICIO] Contenido:', contenido)

            if comando == "rpts1repsa":
                fecha_inicio_str, fecha_fin_str = contenido.split('|')

                query = "SELECT id, consulta_id, calificacion, comentarios, fecha_evaluacion FROM evaluaciones"
                params = []
                if fecha_inicio_str and fecha_fin_str:
                    query += " WHERE DATE(fecha_evaluacion) BETWEEN DATE(?) AND DATE(?)"
                    params = [fecha_inicio_str, fecha_fin_str]
                elif fecha_inicio_str and not fecha_fin_str:
                    query += " WHERE DATE(fecha_evaluacion) >= DATE(?)"
                    params = [fecha_inicio_str]
                elif not fecha_inicio_str and fecha_fin_str:
                    query += " WHERE DATE(fecha_evaluacion) <= DATE(?)"
                    params = [fecha_fin_str]

                print('[SERVICIO] Ejecutando consulta...')
                cursor.execute(query, params)
                rows = cursor.fetchall()

                total = len(rows)
                promedio = sum([r[2] for r in rows]) / total if total > 0 else 0
                evaluaciones_json = []
                for r in rows:
                    evaluaciones_json.append({
                        "id": r[0],
                        "consulta_id": r[1],
                        "calificacion": r[2],
                        "comentarios": r[3],
                        "fecha_evaluacion": r[4]
                    })

                reporte = {
                    "total_evaluaciones": total,
                    "promedio_calificacion": promedio,
                    "evaluaciones": evaluaciones_json
                }

                respuesta_json = json.dumps(reporte)
                # Respuesta también con prefijo rpts1 para que el bus sepa reenviarla al cliente
                # Usamos el comando "rpts1respj" (10 chars) para indicar respuesta JSON
                response_command = "rpts1respj"
                full_response = response_command + respuesta_json
                message = f"{len(full_response):05d}{full_response}".encode()

                print('[SERVICIO] Enviando reporte JSON:', respuesta_json)
                sock.sendall(message)
            else:
                print('[SERVICIO] Comando no reconocido.')
        else:
            print('[SERVICIO] Mensaje no pertenece a este servicio.')

finally:
    print('[SERVICIO] Cerrando...')
    conn.close()
    sock.close()
