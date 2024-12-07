import socket
import sys
import sqlite3

# Crear un socket TCP/IP
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Conectar el socket al puerto donde el bus está escuchando
bus_address = ('localhost', 5000)
print(f'Conectando a {bus_address[0]} en el puerto {bus_address[1]}')
sock.connect(bus_address)

# Conectar a la base de datos SQLite
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Crear la tabla de evaluaciones si no existe
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
    # Enviar datos de inicio: puede ser un código de registro como sinitauth1
    # Aquí, por consistencia con el ejemplo original, enviamos sinit como un servicio distinto, e.g. siniteval1
    message = b'00011siniteval1'
    print(f'Enviando: {message}')
    sock.sendall(message)
    sinit = 1

    while True:
        # Esperar la transacción
        print("Esperando transacción...")
        # Primero leemos el tamaño del paquete
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
            # No hacemos nada más, simplemente seguimos a la espera de comandos
            continue

        # Analizar el comando recibido
        comando = data[:10].decode()  # Obtenemos los primeros 10 chars, por ejemplo: "eval1evcas"
        contenido = data[10:]

        # Verificar si el mensaje está dirigido a este servicio
        if comando.startswith("eval1"):
            # Tenemos un comando para evaluación de caso
            # Formato esperado: eval1evcasID_CONSULTA|CALIFICACION|COMENTARIOS
            # Ejemplo: eval1evcas123|5|Muy buena atención
            if comando == "eval1evcas":
                try:
                    datos_str = contenido.decode()
                    # Dividimos por '|', según la especificación:
                    # Entrada (IN): Evaluar Caso - ID de Consulta - Calificación - Comentarios
                    # Ejemplo: "123|5|Muy buena atención"
                    consulta_id_str, calificacion_str, comentarios = datos_str.split('|')
                    consulta_id = int(consulta_id_str)
                    calificacion = int(calificacion_str)

                    # Insertar la evaluación en la base de datos
                    cursor.execute("INSERT INTO evaluaciones (consulta_id, calificacion, comentarios) VALUES (?, ?, ?)", 
                                   (consulta_id, calificacion, comentarios))
                    conn.commit()

                    # Enviar confirmación de recepción
                    # Por ejemplo: "eval1OK" junto al id de la evaluación
                    eval_id = cursor.lastrowid
                    respuesta = f"eval1OK;{eval_id}"
                    # Longitud + respuesta
                    message = f'{len(respuesta):05d}{respuesta}'.encode()
                    print(f'Enviando: {message}')
                    sock.sendall(message)

                except Exception as e:
                    print(f"Error procesando eval1evcas: {e}")
                    respuesta = "eval1ERROR"
                    message = f'{len(respuesta):05d}{respuesta}'.encode()
                    sock.sendall(message)
            else:
                # Comando eval1 no reconocido
                print("Comando eval1 desconocido.")
                respuesta = "eval1ERRORCMD"
                message = f'{len(respuesta):05d}{respuesta}'.encode()
                sock.sendall(message)
        else:
            # No es para este servicio
            print("Solicitud no perteneciente a este servicio.")
            print(data)

finally:
    print('Cerrando el socket...')
    conn.close()
    sock.close()
