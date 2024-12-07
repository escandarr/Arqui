import socket
import sys

# Crear un socket TCP/IP
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Conectar el socket al puerto donde el bus está escuchando
bus_address = ('localhost', 5000)
print('connecting to {} port {}'.format(*bus_address))
sock.connect(bus_address)

def validar_entrada(entrada, tipo):
    if tipo == "int":
        try:
            return int(entrada)
        except ValueError:
            return None
    elif tipo == "usuario":
        if entrada.strip() == "":
            return None
        return entrada
    elif tipo == "descripcion" or tipo == "etiqueta":
        return entrada

#########################SERVICIO DE CASOS#########################################

def casos_cliente(id_usuario, nombre_usuario):
    print("Bienvenido al sistema de casos de Easy Lawyer señor ", nombre_usuario)
    etiqueta = input('Entre etiqueta del caso: ')
    etiqueta = validar_entrada(etiqueta, "etiqueta")

    usuario = nombre_usuario
    usuario = validar_entrada(usuario, "usuario")
    if usuario is None:
        print("Invalid user. Must not be empty.")
    
    descripcion = input('Ingrese la descripcion del caso: ')
    descripcion = validar_entrada(descripcion, "descripcion")

    datos = f"{etiqueta}|{usuario}|{descripcion}|No asignado|{id_usuario}"  # No incluir case_id
    mensaje = f"{len(datos):05}subcscliente".encode() + datos.encode()
    print('sending {!r}'.format(mensaje))
    sock.sendall(mensaje)

    # Esperar la respuesta
    print("Waiting for transaction")
    amount_received = 0
    amount_expected = int(sock.recv(5))

    data = b""
    while amount_received < amount_expected:
        chunk = sock.recv(amount_expected - amount_received)
        amount_received += len(chunk)
        data += chunk
    print("Checking servi answer ...")
    print('received {!r}'.format(data))
    return

def casos_abogado():
    datos = "Solicitando lista de casos"
    mensaje = f"{len(datos):05}subcsabogado".encode() + datos.encode()
    print('sending {!r}'.format(mensaje))
    sock.sendall(mensaje)

    # Esperar la respuesta
    print("Waiting for transaction")
    amount_received = 0
    amount_expected = int(sock.recv(5))

    data = b""
    while amount_received < amount_expected:
        chunk = sock.recv(amount_expected - amount_received)
        amount_received += len(chunk)
        data += chunk
    print("Checking servi answer ...")
    #print('received {!r}'.format(data))
    print(data[14:])
    return

#########################SERVICIO DE CHAT########################

def historial_chat(sender_id, receiver_id):
    service_name = 'msjeschat'
    formatted_request = f'{len(service_name + ":" + str(sender_id) + ":" + str(receiver_id)):05d}{service_name}:{sender_id}:{receiver_id}'.encode()
    print('Requesting chat history: {!r}'.format(formatted_request))
    sock.sendall(formatted_request)

    # Wait for the chat history response
    amount_received = 0
    amount_expected = int(sock.recv(5))
    chat_data = b''
    while amount_received < amount_expected:
        chunk = sock.recv(amount_expected - amount_received)
        if not chunk:
            break
        chat_data += chunk
        amount_received += len(chunk)
    
    print("Received chat history:")
    print(chat_data.decode())
    return

def chat(id_usuario, nombre_usuario):
    try:
        # Simulate obtaining sender_id (you should implement this according to your authentication system)
        sender_id = id_usuario  # Just an example, you should obtain the sender ID appropriately

        while True:
            # Ask the user to enter a message to send to the service
            
            # User enters the message they want to send
            
            # Prepare the message, ensuring that the total length (NNNNN) and the message are encoded correctly
            # Assuming the message is always sent to the "msjes" service
            service_name = 'msjes'
            receiver_id = input('ingrese id para chatear')  # Assuming receiver_id is 2 for example, adjust this according to your needs
            historial_chat(sender_id, receiver_id)
            custom_message = input('Enviar Mensaje: ')
            # Format the message
            formatted_message = f'{len(service_name + "envi:" + str(sender_id) + ":" + str(receiver_id) + ":" + custom_message):05d}{service_name}envi:{sender_id}:{receiver_id}:{custom_message}'  # Including ':' as delimiter
            message = formatted_message.encode()
            
            print('sending {!r}'.format(message))
            sock.sendall(message)

            # Wait for the response
            print("Waiting for transaction")
            amount_received = 0
            amount_expected = int(sock.recv(5))  # Assuming the bus always sends the length first

            data = b''
            while amount_received < amount_expected:
                chunk = sock.recv(amount_expected - amount_received)
                if not chunk:
                    break  # Socket connection might be broken
                data += chunk
                amount_received += len(chunk)
            
            print("Checking service answer ...")
            print('received {!r}'.format(data))

            # If received '00013msjesReceived', request the chat history
            if data.decode() == 'msjesOKenviOK':
                # Request the updated chat history
                print("se recibio")
                historial_chat(sender_id, receiver_id)
                  # Display the received chat history
            if input('Desea salir del chat? (y/n): ') == 'y':
                break
    finally:
        return

#########################SELECCION DEL SERVICIO########################
#####TIPO 1 PARA ABOGADO TIPO 2 PARA CLIENTE#######

def servicios(tipo_usuario, id_usuario, nombre_usuario):
    if tipo_usuario == 1:  #### USUARIO CLIENTE
        try:
            print("PERFIL DE CLIENTE")
            print("Bienvenido ", nombre_usuario)
            while True:
                print("Presione 1 si desea enviar crear un caso")
                print("Presione 2 si desea chatear con un abogado")
                servicio_escogido = input()
                print(servicio_escogido)
                if servicio_escogido == '1':
                    casos_cliente(id_usuario, nombre_usuario)
                elif servicio_escogido == '2':
                    chat(id_usuario, nombre_usuario)
        finally:
            return

    ###########################USUARIO ABOGADO#################################
    elif tipo_usuario == 2:
        try:
            print("PERFIL DE ABOGADO")
            print("Bienvenido ", nombre_usuario)
            while True:
                print("Presione 1 si desea ver los casos")
                print("Presione 2 si desea chatear con un cliente")
                servicio_escogido = input()
                if servicio_escogido == '1':
                    casos_abogado()
                elif servicio_escogido == '2':
                    chat(id_usuario, nombre_usuario)
        finally:
            return

##################AUTENTICACION###########################
try:
    while True:
        # Enviar mensaje de registro o autenticación de usuario al servicio
        seleccion = input('Seleccione 1 si desea ingresar usuario o 2 si desea registrarse: ')
        if seleccion == '2':
            nombre = input('Enter name: ')
            email = input('Enter email: ')
            password = input('Enter password: ')
            tipo_usuario = input('Ingrese clave secreta si usted es un abogado: ')
            datos = f"{nombre}|{email}|{password}|{tipo_usuario}"
            mensaje = f"{len(datos) + 10:05}auth1regus".encode() + datos.encode()  # auth1regus + datos
            print('sending {!r}'.format(mensaje))
            sock.sendall(mensaje)

            # Esperar la respuesta
            print("Waiting for transaction")
            amount_received = 0
            amount_expected = int(sock.recv(5))

            data = b""
            while amount_received < amount_expected:
                chunk = sock.recv(amount_expected - amount_received)
                amount_received += len(chunk)
                data += chunk
            print("Checking server answer ...")
            print('received {!r}'.format(data))

            if data[0:10] == b'auth1OKOK1':
                user_info = data[8:].decode().split(';')
                if len(user_info) == 3:
                    user_id, nombre = user_info[1], user_info[2]
                    servicios(1, user_id, nombre)  # Cliente
            elif data[0:10] == b'auth1OKOK2':
                user_info = data[8:].decode().split(';')
                if len(user_info) == 3:
                    user_id, nombre = user_info[1], user_info[2]
                    servicios(2, user_id, nombre)  # Abogado

        elif seleccion == '1':
            email = input('Enter email: ')
            password = input('Enter password: ')
            datos = f"{email}|{password}"
            mensaje = f"{len(datos) + 10:05}auth1logus".encode() + datos.encode()  # auth1logus + datos
            print('sending {!r}'.format(mensaje))
            sock.sendall(mensaje)

            # Esperar la respuesta
            print("Waiting for transaction")
            amount_received = 0
            amount_expected = int(sock.recv(5))

            data = b""
            while amount_received < amount_expected:
                chunk = sock.recv(amount_expected - amount_received)
                amount_received += len(chunk)
                data += chunk
            print("Checking server answer ...")
            print('received {!r}'.format(data))
            print("LA DATAS ES ", data)
            if data[0:10] == b'auth1OKOK1':
                user_info = data[8:].decode().split(';')
                if len(user_info) == 3:
                    user_id, nombre = user_info[1], user_info[2]
                    servicios(1, user_id, nombre)  # Cliente
            elif data[0:10] == b'auth1OKOK2':
                user_info = data[8:].decode().split(';')
                print("entro?")
                if len(user_info) == 3:
                    user_id, nombre = user_info[1], user_info[2]
                    servicios(2, user_id, nombre)  # Abogado

finally:
    print('closing socket')
    sock.close()
