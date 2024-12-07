import socket
import sqlite3
###################################################################################
##########################AQUI SE PROCESA LA TRANSACCION############################
###################################################################################


def handle_transaction(data):
    try:
        # Extraer el nombre del servicio y los datos
        service_name = data[:5].decode()
        content = data[5:]

        # Revisar si la operación es almacenar o recuperar datos
        operation = content[:5].decode()
        if operation == 'store':
            # Extraer el mensaje
            print("solicitud de store")
            rest_of_content = content[5:].decode()
            parts = list(filter(None, rest_of_content.split(':', 3)))

            print(rest_of_content)
            print(parts)  # Separar sender_id, receiver_id y mensaje usando ':'
            if len(parts) == 3:  # Asegurarse de que hay tres partes (sender_id, receiver_id, mensaje)
                sender_id, receiver_id, message = parts
                save_message(sender_id, receiver_id, message)
                response = f'{len("dbsrvstoreOK"):05d}dbsrvstoreOK'
            else:
                response = f'{len("error2"):05d}error2'
        elif operation == 'fetch':
            print("solicitud de fetch")
            messages = fetch_messages()
            messages_str = "\n".join(messages)
            response_content = f'dbsrvfetchOK{messages_str}'
            response = f'{len(response_content):05d}{response_content}'
        else:
            response = f'{len("errorNK"):05d}errorNK'
    except Exception as e:
        print(f"Error handling transaction: {e}")
        response = f'{len("errorNK"):05d}errorNK'
    return response.encode()


#####################################################################
########################## TRANSACCIONES ############################
#####################################################################


def save_message(sender_id, receiver_id, message):
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO messages (sender_id, receiver_id, message) VALUES (?, ?, ?)', (sender_id, receiver_id, message))
        conn.commit()
    finally:
        conn.close()


# Función para recuperar mensajes de la base de datos
def fetch_messages():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT sender_id, receiver_id, message FROM messages')
    rows = cursor.fetchall()
    conn.close()
    return [f"Sender: {row[0]}, Receiver: {row[1]}, Message: {row[2]}" for row in rows]



######################################################################
########################## INICIALIZACION ############################
######################################################################

# Inicialización del servidor de base de datos
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Conectar el socket al puerto donde el bus está escuchando
bus_address = ('localhost', 5000)
print('Conectando a {} puerto {}'.format(*bus_address))
sock.connect(bus_address)

try:
    # Enviar mensaje de inicialización al bus
    message = b'00010sinitdbsrv'
    print('Enviando {!r}'.format(message))
    sock.sendall(message)
    sinit = 1

    while True:
        # Esperar la transacción desde el bus
        print("Esperando transacción")
        amount_received = 0
        amount_expected = int(sock.recv(5))
        data = b''
        while amount_received < amount_expected:
            chunk = sock.recv(amount_expected - amount_received)
            if not chunk:
                break
            data += chunk
            amount_received += len(chunk)

        service_name = data[:5].decode()  # Extraer el nombre del servicio

        # Verificar si el mensaje está dirigido al servicio de base de datos
        if service_name == 'dbsrv':
            print(f"Received data: {data}")  # Imprimir cuando se recibe una petición válida
            response = handle_transaction(data)
            # Enviar la respuesta de vuelta al bus
            print('Enviando respuesta {!r}'.format(response))
            sock.sendall(response)

        if sinit == 1:
            sinit = 0
            print('Respuesta de inicialización recibida')

finally:
    print('Cerrando el socket')
    sock.close()