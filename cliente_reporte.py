import socket
import sys

# Crear un socket TCP/IP
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Conectar el socket al puerto donde el bus está escuchando
bus_address = ('localhost', 5000)
print('connecting to {} port {}'.format(*bus_address))
sock.connect(bus_address)


def iniciar_sesion():
    """
    Función para autenticar al usuario.
    """
    email = input('Ingrese su email: ')
    password = input('Ingrese su contraseña (no la clave secreta): ')
    datos = f"{email}|{password}"
    mensaje = f"{len(datos) + 10:05}auth1logus".encode() + datos.encode()
    print('Enviando datos de inicio de sesión...')
    sock.sendall(mensaje)

    # Esperar respuesta del servicio de autenticación
    print("Esperando respuesta del servicio de autenticación...")
    amount_received = 0
    amount_expected = int(sock.recv(5))

    data = b""
    while amount_received < amount_expected:
        chunk = sock.recv(amount_expected - amount_received)
        amount_received += len(chunk)
        data += chunk

    print("Respuesta del servicio de autenticación:")
    print(data.decode())
    if data[0:10] == b'auth1OKOK1':
        user_info = data[8:].decode().split(';')
        if len(user_info) == 3:
            return int(user_info[1]), user_info[2], 1  # Cliente
    elif data[0:10] == b'auth1OKOK2':
        user_info = data[8:].decode().split(';')
        if len(user_info) == 3:
            return int(user_info[1]), user_info[2], 2  # Abogado
    else:
        print("Error al iniciar sesión.")
        return None, None, None


def generar_reporte():
    """
    Solicita al servicio de reportes generar un reporte para un caso específico.
    """
    consulta_id = input("Ingrese el ID del caso para generar el reporte: ")
    if not consulta_id.isdigit():
        print("El ID de la consulta debe ser un número.")
        return

    consulta_id = int(consulta_id)
    service_name = "repor"
    datos = f"{consulta_id}"
    mensaje = f"{len(datos) + len(service_name):05}{service_name}{datos}".encode()
    print('Enviando solicitud para generar reporte...')
    sock.sendall(mensaje)

    # Esperar la respuesta del servicio de reportes
    print("Esperando respuesta del servicio de reportes...")
    amount_received = 0
    amount_expected = int(sock.recv(5))

    data = b""
    while amount_received < amount_expected:
        chunk = sock.recv(amount_expected - amount_received)
        amount_received += len(chunk)
        data += chunk

    print("Respuesta del servicio de reportes:")
    print(data.decode())


def historial_reportes():
    """
    Solicita al servicio de reportes el historial de reportes para un caso específico.
    """
    consulta_id = input("Ingrese el ID del caso para ver el historial de reportes: ")
    if not consulta_id.isdigit():
        print("El ID de la consulta debe ser un número.")
        return

    consulta_id = int(consulta_id)
    service_name = "histreportes"
    datos = f"{consulta_id}"
    mensaje = f"{len(datos) + len(service_name):05}{service_name}{datos}".encode()
    print('Enviando solicitud para obtener historial de reportes...')
    sock.sendall(mensaje)

    # Esperar la respuesta del servicio de reportes
    print("Esperando respuesta del servicio de reportes...")
    amount_received = 0
    amount_expected = int(sock.recv(5))

    data = b""
    while amount_received < amount_expected:
        chunk = sock.recv(amount_expected - amount_received)
        amount_received += len(chunk)
        data += chunk

    print("Respuesta del servicio de reportes:")
    print(data.decode())


def menu_reportes():
    """
    Menú principal para gestionar reportes.
    """
    print("Bienvenido al cliente de reportes")
    user_id, nombre_usuario, tipo_usuario = iniciar_sesion()
    if user_id is None:
        print("No se pudo iniciar sesión. Saliendo...")
        return

    print(f"Bienvenido {nombre_usuario}. Su tipo de usuario es {'Cliente' if tipo_usuario == 1 else 'Abogado'}.")

    while True:
        print("\nOpciones:")
        print("1. Generar un reporte de caso")
        print("2. Consultar historial de reportes")
        print("3. Salir")
        opcion = input("Seleccione una opción: ")

        if opcion == "1":
            generar_reporte()
        elif opcion == "2":
            historial_reportes()
        elif opcion == "3":
            print("Saliendo del cliente de reportes. ¡Hasta luego!")
            break
        else:
            print("Opción no válida. Intente nuevamente.")


if __name__ == "__main__":
    try:
        menu_reportes()
    finally:
        print('Cerrando conexión...')
        sock.close()
