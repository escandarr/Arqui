import socket

# Datos para solicitar el reporte
fecha_inicio = input("Ingrese la fecha de inicio (YYYY-MM-DD) o deje en blanco para no filtrar por inicio: ").strip()
fecha_fin = input("Ingrese la fecha de fin (YYYY-MM-DD) o deje en blanco para no filtrar por fin: ").strip()

comando = "repsatisfa"
payload = f"{fecha_inicio}|{fecha_fin}"
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
    print(f'Enviando solicitud de reporte: {mensaje}')
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
        print("Reporte recibido (JSON):")
        print(respuesta) 
finally:
    print('Cerrando el socket del cliente...')
    sock.close()
