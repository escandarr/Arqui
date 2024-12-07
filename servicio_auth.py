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

# Crear la tabla de usuarios si no existe
cursor.execute('''
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        es_abogado INTEGER NOT NULL DEFAULT 0  -- Añadir campo para indicar si el usuario es abogado
    )
''')
conn.commit()

try:
    # Enviar datos de inicio
    message = b'00010sinitauth1'
    print(f'Enviando: {message}')
    sock.sendall(message)
    sinit = 1

    while True:
        # Esperar la transacción
        print("Esperando transacción...")
        amount_received = 0
        amount_expected = int(sock.recv(5))

        data = b""
        while amount_received < amount_expected:
            chunk = sock.recv(amount_expected - amount_received)
            amount_received += len(chunk)
            data += chunk
        
        # Verificar si es la respuesta de inicialización
        if sinit == 1:
            sinit = 0
            print('Respuesta de sinit recibida')
            
        # Verificar si el mensaje está dirigido a este servicio
        elif data[:5].decode() == 'auth1':
            print("Procesando ...")
            print(f'Recibido: {data}')
            
            comando = data[:10].decode()  # auth1regus o auth1logus
            datos = data[10:]
            if comando == "auth1regus":
                try:
                    nombre, email, password, clave = datos.decode().split('|')
                    print(f"Procesando AUTH1REGUS: nombre={nombre}, email={email}, password={password}, clave={clave}")

                    es_abogado = 1 if clave == "soyabogado" else 0

                    cursor.execute("SELECT id FROM usuarios WHERE email = ?", (email,))
                    if cursor.fetchone() is not None:
                        respuesta = f"El usuario con email {email} ya existe."
                        message = b'00018auth1OKEXISTE'
                        print(f'Enviando: {message}')
                        sock.sendall(message)   
                    else:
                        cursor.execute("INSERT INTO usuarios (nombre, email, password, es_abogado) VALUES (?, ?, ?, ?)", (nombre, email, password, es_abogado))
                        conn.commit()
                        cursor.execute("SELECT id FROM usuarios WHERE email = ?", (email,))
                        user_id = cursor.fetchone()[0]
                        respuesta = f"Usuario {nombre} registrado exitosamente."
                        print(f"Insertado en la base de datos: nombre={nombre}, email={email}, password={password}, es_abogado={es_abogado}")
                        
                        if es_abogado:
                            message = f'{len("auth1OK2") + len(str(user_id)) + len(nombre) + 2:05d}auth1OK2;{user_id};{nombre}'.encode()
                        else:
                            message = f'{len("auth1OK1") + len(str(user_id)) + len(nombre) + 2:05d}auth1OK1;{user_id};{nombre}'.encode()
                        
                        print(f'Enviando: {message}')
                        sock.sendall(message)   
                except Exception as e:
                    respuesta = f"Error procesando AUTH1REGUS: {e}"
                    print(f"Error: {e}")
            elif comando == "auth1logus":
                try:
                    email, password = datos.decode().split('|')
                    print(f"Procesando AUTH1LOGUS: email={email}, password={password}")

                    cursor.execute("SELECT id, nombre, es_abogado FROM usuarios WHERE email = ? AND password = ?", (email, password))
                    user = cursor.fetchone()
                    if user is not None:
                        user_id, nombre, es_abogado = user
                        respuesta = f"Usuario {nombre} autenticado exitosamente."
                        
                        if es_abogado:
                            message = f'{len("auth1OK2") + len(str(user_id)) + len(nombre) + 2:05d}auth1OK2;{user_id};{nombre}'.encode()
                        else:
                            message = f'{len("auth1OK1") + len(str(user_id)) + len(nombre) + 2:05d}auth1OK1;{user_id};{nombre}'.encode()
                        
                        print(f'Enviando: {message}')
                        sock.sendall(message) 
                    else:
                        respuesta = "Error de autenticación. Usuario o contraseña incorrectos."
                        message = b'00019auth1NOEXISTENK'
                        print(f'Enviando: {message}')
                        sock.sendall(message) 
                except Exception as e:
                    respuesta = f"Error procesando AUTH1LOGUS: {e}"
                    print(f"Error: {e}")
            else:
                respuesta = "Comando no reconocido."
        else:
            print("Solicitud no perteneciente a este servicio.")
            print(data)
finally:
    print('Cerrando el socket...')
    conn.close()
    sock.close()
