import socket

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect the socket to the port where the bus is listening
bus_address = ('localhost', 5000)
print('Conectando a {} puerto {}'.format(*bus_address))
sock.connect(bus_address)

try:
    # Enviar datos de inicialización al bus
    message = b'00010sinitmsjes'
    print('Enviando {!r}'.format(message))
    sock.sendall(message)
    sinit = 1

    mensajes_recibidos = []  # Lista para almacenar los mensajes

    while True:
        # Esperar la respuesta del bus
        print("Esperando transacción")
        amount_received = 0
        amount_expected = int(sock.recv(5))
        data = b''
        while amount_received < amount_expected:
            chunk = sock.recv(amount_expected - amount_received)
            data += chunk
            amount_received += len(chunk)

        service_name = data[:5].decode()  # Extraer el nombre del servicio
        service_name2 = data[:9].decode()  # Extraer el tipo de solicitud

        # Verificar el tipo de solicitud recibida
        if service_name2 == 'msjesenvi':
            # Mensaje de envío de mensaje (msjesenvi)
            mensaje = data[10:].decode()  # Extraer solo el mensaje sin el nombre del servicio y 'env'
            parts = mensaje.split(':', 2)  # Separar sender, receiver, mensaje usando ':'
            if len(parts) == 3:
                sender, receiver, message = parts
                print("Procesando msjesenvi...")
                print('Recibida solicitud de mensajes')
                print('Sender:', sender)
                print('Receiver:', receiver)
                print('Mensaje:', message)

                # Simular el almacenamiento del mensaje en la base de datos
                # Aquí puedes implementar la lógica real para almacenar en tu base de datos
                db_message = f'{len("dbsrvstore:" + sender + ":" + receiver + ":" + message):05d}dbsrvstore:{sender}:{receiver}:{message}'.encode()
                print('Enviando mensaje a dbsrv {!r}'.format(db_message))
                sock.sendall(db_message)
                db_response_length = int(sock.recv(5))
                db_response = sock.recv(db_response_length)
                print('Respuesta de dbsrv {!r}'.format(db_response))

                # Simular una respuesta al cliente
                response = b'00010msjesenviOK'
                print('Enviando respuesta {!r}'.format(response))
                sock.sendall(response)

        elif service_name2 == 'msjeschat':
            # Mensaje de solicitud de historial de chat (msjeschat)
            users_ids = data[10:].decode()  # Extraer sender y receiver sin el nombre del servicio y 'chat'
            sender, receiver = users_ids.split(':', 1)  # Separar sender y receiver usando ':'
            print("Procesando msjeschat...")
            print('Recibida solicitud de chat')
            print('Sender ID:', sender)
            print('Receiver ID:', receiver)

            # Simular la recuperación del historial de chat desde la base de datos
            # Aquí puedes implementar la lógica real para recuperar el historial de chat
            # Simulamos la consulta a la base de datos para obtener el historial de chat
            db_request = f'{len("dbsrvfetch:" + sender + ":" + receiver + ":10"):05d}dbsrvfetch:{sender}:{receiver}:10'.encode()
            print('Enviando solicitud de historial de chat a dbsrv {!r}'.format(db_request))
            sock.sendall(db_request)

            # Recibir la respuesta de la base de datos
            db_response_length = int(sock.recv(5))
            db_response = sock.recv(db_response_length)
            print('Respuesta de dbsrv {!r}'.format(db_response))

            # Enviar la respuesta al cliente
            response = f'{len("msjeschat") + len(db_response):05d}msjeschat'.encode() + db_response
            print('Enviando respuesta a cliente {!r}'.format(response))
            sock.sendall(response)

        if sinit == 1:
            sinit = 0
            print('Respuesta de inicialización recibida')

        # Imprimir todos los mensajes recibidos hasta el momento, con los nombres de usuario, separados por un salto de línea
        print("\n".join(mensajes_recibidos))

finally:
    print('Cerrando el socket')
    sock.close()
