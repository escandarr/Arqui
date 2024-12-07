import socket

BUS_HOST = 'localhost'
BUS_PORT = 5000

fecha_inicio = input("Ingrese la fecha de inicio (YYYY-MM-DD) o deje en blanco: ").strip()
fecha_fin = input("Ingrese la fecha de fin (YYYY-MM-DD) o deje en blanco: ").strip()

comando = "rpts1repsa"  # 10 caracteres
payload = f"{fecha_inicio}|{fecha_fin}"
mensaje = comando + payload

longitud = len(mensaje)
cabecera = f"{longitud:05d}"
message = (cabecera + mensaje).encode()

print("[CLIENTE] Conectando al bus...")
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((BUS_HOST, BUS_PORT))
print("[CLIENTE] Conexión establecida con el bus.")

try:
    print("[CLIENTE] Enviando solicitud:", mensaje)
    sock.sendall(message)

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
        # Respuesta tendrá el formato: rpts1respj{JSON}
        # Los primeros 10 caracteres son 'rpts1respj', el resto es el JSON
        if respuesta.startswith("rpts1respj"):
            json_response = respuesta[10:]
            print("[CLIENTE] Reporte recibido (JSON):")
            print(json_response)
        else:
            print("[CLIENTE] Respuesta con formato inesperado:", respuesta)
    else:
        print("[CLIENTE] No se recibió respuesta del servicio.")

finally:
    print("[CLIENTE] Cerrando conexión...")
    sock.close()
