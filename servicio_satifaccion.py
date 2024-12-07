import socket
import sys
import sqlite3
import json
from datetime import datetime

# Crear un socket TCP/IP
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Conectar el socket al puerto donde el bus está escuchando
bus_address = ('localhost', 5000)
print(f'Conectando a {bus_address[0]} en el puerto {bus_address[1]}')
sock.connect(bus_address)

# Conectar a la base de datos SQLite
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

try:
    # Enviar datos de inicio para el servicio de reporte de satisfacción
    message = b'00013sinitreport'
    print(f'Enviando: {message}')
    sock.sendall(message)
    sinit = 1

    while True:
        # Esperar la transacción
        print("Esperando transacción...")
        size_data = sock.recv(5)
        if not size_data:
            break
        amount_expected = int(size_data)

        data = b""
        amount_received = 0
        while amount_received < amount_expected:
            chunk = sock.recv(amount_expected - amount_received)
            if not chunk:
                break
            amount_received += len(chunk)
            data += chunk

        if sinit == 1:
            # Respuesta a la inicialización
            sinit = 0
            print('Respuesta de sinit recibida')
            continue

        # Analizar el comando recibido
        comando = data[:10].decode()
        contenido = data[10:]

        if comando == "repsatisfa":
            # Formato esperado (flexible): repsatisfaYYYY-MM-DD|YYYY-MM-DD
            # Si fechas vacías => mostrar todos los reportes
            # Si fecha_inicio vacía => hasta fecha_fin
            # Si fecha_fin vacía => desde fecha_inicio
            try:
                datos_str = contenido.decode()
                # Podría ser ""|"", "2023-01-01"|"" o ""|"2023-12-31" o ambas fechas
                fecha_inicio_str, fecha_fin_str = datos_str.split('|')

                query = "SELECT id, consulta_id, calificacion, comentarios, fecha_evaluacion FROM evaluaciones"
                params = []

                # Construir dinámica la consulta según las fechas
                if fecha_inicio_str and fecha_fin_str:
                    # Ambas fechas presentes
                    query += " WHERE DATE(fecha_evaluacion) BETWEEN DATE(?) AND DATE(?)"
                    params = [fecha_inicio_str, fecha_fin_str]
                elif fecha_inicio_str and not fecha_fin_str:
                    # Solo fecha de inicio
                    query += " WHERE DATE(fecha_evaluacion) >= DATE(?)"
                    params = [fecha_inicio_str]
                elif not fecha_inicio_str and fecha_fin_str:
                    # Solo fecha de fin
                    query += " WHERE DATE(fecha_evaluacion) <= DATE(?)"
                    params = [fecha_fin_str]
                # Si ambas están vacías, no se agrega WHERE (trae todo)

                cursor.execute(query, params)
                rows = cursor.fetchall()

                # Calcular estadísticas
                total = len(rows)
                if total > 0:
                    promedio = sum([r[2] for r in rows]) / total
                else:
                    promedio = 0

                # Armar estructura JSON
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

                # Enviar la respuesta
                message = f"{len(respuesta_json):05d}{respuesta_json}".encode()
                print(f'Enviando reporte: {respuesta_json}')
                sock.sendall(message)

            except Exception as e:
                print(f"Error procesando repsatisfa: {e}")
                respuesta = "repsatisfaERROR"
                message = f'{len(respuesta):05d}{respuesta}'.encode()
                sock.sendall(message)
        else:
            # No es para este servicio
            print("Solicitud no perteneciente a este servicio.")
            print(data)

finally:
    print('Cerrando el socket del servicio de reporte...')
    conn.close()
    sock.close()
