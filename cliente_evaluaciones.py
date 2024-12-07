import socket

# Pedir datos al usuario por terminal
consulta_id = input("Ingrese el ID de la consulta a evaluar: ")
calificacion = input("Ingrese una calificación (por ejemplo, del 1 al 5): ")
comentarios = input("Ingrese sus comentarios sobre la atención recibida: ")

# Preparar el mensaje
# Formato: eval1evcas + "consulta_id|calificacion|comentarios"
comando = "eval1evcas"
payload = f"{consulta_id}|{calificacion}|{comentarios}"
mensaje = comando + payload

# Calculamos la longitud
longitud = len(mensaje)
cabecera = f"{longitud:05d}"

# Mensaje final a enviar
message = (cabecera + mensaje).encode()

# Crear socket para el cliente
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
bus_address = ('localhost', 5000)
print(f'Conectando a {bus_address}')
sock.connect(bus_address)

try:
    print(f'Enviando: {mensaje}')
    sock.sendall(message)

    # Recibir respuesta del servicio
    size_data = sock.recv(5)
    if size_data:
        amount_expected = int(size_data)
        data = b""
        amount_received = 0
        while amount_received < amount_expected:
            chunk = sock.recv(amount_expected - amount_received)
            if not chunk:
                break
            amount_received += len(chunk)
            data += chunk

        respuesta = data.decode()
        print(f"Respuesta recibida: {respuesta}")

finally:
    print('Cerrando el socket del cliente...')
    sock.close()
