# 🛫 Buscador de Vuelos con Notificación 📲

Este proyecto es una aplicación de búsqueda de vuelos que utiliza la API de SerpAPI para obtener información sobre vuelos y envía notificaciones por WhatsApp utilizando Twilio. La aplicación incluye una interfaz gráfica creada con Tkinter.

## ✈️ Características

- 🔍 Búsqueda de vuelos basada en los parámetros de salida, llegada y fechas.
- 💱 Conversión de precios de EUR a COP.
- 📩 Envío de notificaciones por WhatsApp cuando se encuentra el vuelo más económico.
- 🗂 Almacenamiento y visualización de datos históricos de los vuelos.
- 🖥 Interfaz gráfica con Tkinter para la entrada de datos y la visualización de resultados.

## 📋 Requisitos

- Python 3.x
- Bibliotecas de Python: `requests`, `twilio`, `tkinter`, `tkcalendar`, `pandas`, `numpy`
- Cuenta de Twilio y sus credenciales (Account SID, Auth Token, Números de WhatsApp)
- Cuenta de SerpAPI y su API key
- (BUSCANDO API QUE PERMITA NOTIFICACIONES INFINITAS)

## 🛠 Instalación

1. Clona este repositorio.
2. Instala las bibliotecas requeridas:
    ```bash
    pip install requests twilio tkcalendar pandas numpy
    ```

3. Configura tus variables de entorno:
    ```bash
    export TWILIO_ACCOUNT_SID='tu_SID_de_cuenta'
    export TWILIO_AUTH_TOKEN='tu_token_de_autenticación'
    export TWILIO_WHATSAPP_NUMBER='whatsapp:+tu_número_de_Twilio'
    export TWILIO_TO_WHATSAPP_NUMBER='whatsapp:+tu_número_de_WhatsApp'
    ```

## 🚀 Uso

1. Configura los parámetros de Twilio en el archivo `buscador_vuelos.py` utilizando variables de entorno:
    ```python
    ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
    AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
    FROM_WHATSAPP_NUMBER = os.getenv('TWILIO_WHATSAPP_NUMBER')
    TO_WHATSAPP_NUMBER = os.getenv('TWILIO_TO_WHATSAPP_NUMBER')
    ```

2. Ejecuta la aplicación:
    ```bash
    python buscador_vuelos.py
    ```

3. Ingresa los datos de salida, llegada, fecha de salida y fecha de regreso en la interfaz gráfica.

4. La aplicación buscará vuelos y enviará notificaciones por WhatsApp cuando se encuentre el vuelo más económico. Los datos históricos se visualizarán en una ventana separada.

## 📄 Código

### Búsqueda de Datos de Vuelos

```python
def fetch_flight_data(params):
    """Realiza la solicitud a la API de SerpAPI y devuelve los datos de vuelo."""
    try:
        response = requests.get(API_URL, params=params)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error en la solicitud: {e}")
        if response is not None:
            print(response.text)  # Imprimir el cuerpo de la respuesta para más detalles
        return None
```
### Procesamiento de Datos de Vuelos
```python
def process_flight_data(data):
    """Procesa los datos de vuelo y devuelve una lista de detalles de los vuelos."""
    flight_details = []
    best_flights = data.get('best_flights', [])

    if not best_flights:
        print("No se encontraron vuelos en esta iteración.")
        return flight_details

    for flight in best_flights:
        try:
            price_in_eur = flight.get('price', 0)
            price_in_cop = price_in_eur * EUR_TO_COP_RATE

            if price_in_cop <= 0:
                continue

            airline = flight['flights'][0].get('airline', 'Unknown')
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            flight_details.append((price_in_cop, airline, timestamp))

            print(f"Precio: {price_in_cop} COP")
            print(f"Aerolínea: {airline}")
            print(f"Hora: {timestamp}")
            print("-" * 40)
        except KeyError as e:
            print(f"Clave faltante en el diccionario: {e}")

    return flight_details
```

### Envio de notificacion por whatsapp
```python
def send_whatsapp_notification(price, airline):
    """Envía una notificación de WhatsApp con el precio y la aerolínea más económica."""
    message_body = (f"Nuevo precio más económico a SANTA MARTA encontrado: {price} COP "
                    f"con {airline}.")

    message = TWILIO_CLIENT.messages.create(
        body=message_body,
        from_=FROM_WHATSAPP_NUMBER,
        to=TO_WHATSAPP_NUMBER
    )

    print(f"Notificación enviada a WhatsApp: {message.sid}")


```

###📝 Notas
Actualiza la tasa de conversión EUR a COP (EUR_TO_COP_RATE) según sea necesario.

Configura los parámetros de búsqueda en la función search_flights.

###👏 Créditos
Twilio para el envío de mensajes por WhatsApp.

SerpAPI para la búsqueda de vuelos.

Tkinter para la interfaz gráfica.

¡Espero que esto te sea útil! 🚀

