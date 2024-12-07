### **README: Sistema LegalConsult**

Este proyecto implementa un sistema distribuido para gestionar consultas legales, comunicación entre clientes y abogados, y otras funcionalidades relacionadas. El sistema está compuesto por múltiples servicios conectados a través de un bus de mensajes.

---

### **Requerimientos Funcionales (RF) y Pruebas**

A continuación, se describen los Requerimientos Funcionales (RF) y cómo probarlos desde la terminal.

---

#### **RF-01: Gestión de Usuarios**

1. **Registrar Usuario (Cliente o Abogado)**
   - **Descripción**: Permite registrar clientes o abogados en el sistema.
   - **Prueba**:
     1. Ejecuta el cliente:
        ```bash
        python cliente.py
        ```
     2. Selecciona la opción `2` para registrar un usuario.
     3. Introduce los datos solicitados:
        - Nombre
        - Email
        - Contraseña
        - Clave secreta (solo si eres abogado; usa `soyabogado`).
     4. Verifica la confirmación de registro en la terminal.

2. **Autenticar Usuario**
   - **Descripción**: Permite iniciar sesión como cliente o abogado.
   - **Prueba**:
     1. Ejecuta el cliente:
        ```bash
        python cliente.py
        ```
     2. Selecciona la opción `1` para iniciar sesión.
     3. Introduce el email y la contraseña.
     4. Verifica el mensaje de éxito o error.

---

#### **RF-02: Gestión de Consultas**

1. **Registrar Consulta (Cliente)**
   - **Descripción**: Los clientes pueden registrar consultas legales especificando detalles como etiqueta, descripción y área del derecho.
   - **Prueba**:
     1. Inicia sesión como cliente.
     2. Selecciona la opción `1` para registrar un caso.
     3. Introduce los datos solicitados:
        - Etiqueta: "Caso laboral".
        - Descripción: "Problema con contrato".
        - Área del Derecho: "Laboral".
     4. Verifica la confirmación de registro.

2. **Listar Consultas (Abogado)**
   - **Descripción**: Los abogados pueden listar las consultas disponibles para aceptarlas.
   - **Prueba**:
     1. Inicia sesión como abogado.
     2. Selecciona la opción `1` para listar los casos.
     3. Verifica que se muestran los detalles de los casos en la terminal.

---

#### **RF-03: Servicio de Mensajería**

1. **Enviar Mensaje**
   - **Descripción**: Permite a los clientes y abogados comunicarse a través de mensajes.
   - **Prueba**:
     1. Inicia sesión como cliente o abogado.
     2. Selecciona la opción `2` para abrir el chat.
     3. Observa la lista de abogados disponibles con sus IDs.
     4. Introduce el ID del abogado con quien deseas chatear.
     5. Escribe un mensaje.
     6. Verifica la confirmación de envío.

2. **Consultar Historial de Chat**
   - **Descripción**: Permite consultar el historial de mensajes con un usuario específico.
   - **Prueba**:
     1. Sigue los pasos de "Enviar Mensaje".
     2. Verifica que el historial se muestra antes de enviar nuevos mensajes.

---

#### **RF-04: Reportes de Progreso**

1. **Generar Reporte**
   - **Descripción**: Genera un reporte detallado del progreso del caso.
   - **Prueba**:
     1. Inicia sesión como cliente o abogado.
     2. Solicita un reporte de progreso ingresando el ID del caso.
     3. Verifica el reporte en formato JSON en la terminal.

2. **Historial de Reportes**
   - **Descripción**: Permite consultar reportes pasados de un caso.
   - **Prueba**:
     1. Inicia sesión como cliente o abogado.
     2. Solicita el historial de reportes para un caso específico.
     3. Verifica los reportes en la terminal.

---

#### **RF-05: Evaluación de Casos**

1. **Evaluar Caso**
   - **Descripción**: Los clientes pueden calificar un caso finalizado.
   - **Prueba**:
     1. Inicia sesión como cliente.
     2. Introduce el ID del caso finalizado.
     3. Proporciona una calificación (1-5) y comentarios.
     4. Verifica la confirmación de evaluación.

---

#### **RF-06: Gestión de Agendas**

1. **Crear Agenda**
   - **Descripción**: Los abogados pueden registrar su disponibilidad.
   - **Prueba**:
     1. Inicia sesión como abogado.
     2. Registra horarios disponibles para consultas.
     3. Verifica la confirmación en la terminal.

2. **Consultar Agenda**
   - **Descripción**: Los clientes pueden ver la agenda de un abogado.
   - **Prueba**:
     1. Inicia sesión como cliente.
     2. Solicita la agenda de un abogado específico ingresando su ID.
     3. Verifica la agenda en formato JSON en la terminal.

---

#### **RF-08: Reporte de Satisfacción**

1. **Generar Reporte de Satisfacción**
   - **Descripción**: Genera un reporte de satisfacción basado en evaluaciones de clientes.
   - **Prueba**:
     1. Inicia sesión como administrador (si el sistema soporta roles admin).
     2. Solicita un reporte ingresando un rango de fechas (e.g., "2023-01-01" a "2023-12-31").
     3. Verifica el reporte en formato JSON.

---

### **Configuración del Sistema**

1. **Inicializar el Bus**:
   ```bash
   docker network create soa
   docker run -d -p 5000:5000 --name soabus --network soa jrgiadach/soabus:v1
   ```

2. **Ejecutar los Servicios**:
   Construye y ejecuta los servicios necesarios:
   ```bash
   docker build -t servicio_casos .
   docker run -d --network soa --name servicio_casos servicio_casos

   docker build -t servicio_auth .
   docker run -d --network soa --name servicio_auth servicio_auth
   ```

3. **Ejecutar el Cliente**:
   ```bash
   python cliente.py
   ```

---

### **Notas**
- Asegúrate de tener configurada correctamente la red Docker (`soa`) para conectar todos los servicios.
- Para verificar logs o errores, revisa las salidas de cada contenedor con:
  ```bash
  docker logs <nombre_del_contenedor>
  ```
