import os
import requests
import time
from twilio.rest import Client
import tkinter as tk
from tkinter import messagebox, Toplevel, Text, Button
from tkcalendar import DateEntry
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

# Definimos la URL base de la API de SerpAPI
API_URL = "https://serpapi.com/search"

# Tasa de conversión EUR a COP
EUR_TO_COP_RATE = 4300  # Actualizar esta tasa según sea necesario

# Configuración de Twilio (utilizando variables de entorno)
ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')  # SID de cuenta de Twilio
AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')    # Token de autenticación de Twilio
TWILIO_CLIENT = Client(ACCOUNT_SID, AUTH_TOKEN)
FROM_WHATSAPP_NUMBER = os.getenv('TWILIO_WHATSAPP_NUMBER')  # Número de Twilio
TO_WHATSAPP_NUMBER = os.getenv('TWILIO_TO_WHATSAPP_NUMBER')  # Número de WhatsApp

# Lista para almacenar datos históricos
historic_data = []

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

def filter_and_store_data(flight_details):
    """Filtra y almacena los datos cada 30 segundos, guardando solo el valor mínimo."""
    df = pd.DataFrame(flight_details, columns=['price', 'airline', 'timestamp'])
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['seconds_elapsed'] = (df['timestamp'] - df['timestamp'].iloc[0]).dt.total_seconds()
    df['interval'] = np.floor(df['seconds_elapsed'] / 30) * 30
    filtered_df = df.groupby('interval').agg({'price': 'min', 'airline': 'first', 'timestamp': 'first'}).reset_index()
    return filtered_df

def search_flights():
    """Función que ejecuta la búsqueda de vuelos y actualiza la interfaz gráfica."""
    departure = departure_var.get()
    arrival = arrival_var.get()
    outbound_date = outbound_date_entry.get()
    return_date = return_date_entry.get()

    # Revisar si las fechas son válidas
    if not outbound_date or not return_date:
        messagebox.showerror("Error", "Por favor, ingresa fechas válidas.")
        return
    if outbound_date >= return_date:
        messagebox.showerror("Error", "La fecha de regreso debe ser después de la fecha de salida.")
        return

    params = {
        "engine": "google_flights",
        "q": f"Flights to {arrival} from {departure} on {outbound_date} through {return_date}",
        "hl": "en",
        "gl": "co",
        "departure_id": departure,
        "arrival_id": arrival,
        "outbound_date": outbound_date,
        "return_date": return_date,
        "api_key": "8644bc23b67ae41015a3f5e7fcb1b546c1192986242d5dba7d75e657447de7e8"
    }

    flight_details = []
    data = fetch_flight_data(params)

    if data:
        flight_details.extend(process_flight_data(data))

    if flight_details:
        filtered_data = filter_and_store_data(flight_details)
        if not filtered_data.empty:
            min_price, min_airline, timestamp = filtered_data.iloc[-1][['price', 'airline', 'timestamp']]
            historic_data.append((min_price, min_airline, timestamp))
            send_whatsapp_notification(min_price, min_airline)
            result_text.set(f"El precio más económico encontrado es: {min_price} COP\n"
                            f"Aerolínea del vuelo más económico: {min_airline}\n"
                            f"Hora: {timestamp}")
            update_external_window(historic_data)
        else:
            result_text.set("No se encontraron vuelos válidos.")
            update_external_window(historic_data)

    root.after(30000, search_flights)  # Programar la próxima actualización en 30 segundos

def update_external_window(historic_data):
    """Actualiza la ventana externa con los datos históricos de los vuelos."""
    external_text.config(state=tk.NORMAL)  # Habilitar el widget de texto para editar
    external_text.delete(1.0, tk.END)  # Borrar el contenido anterior
    for price, airline, timestamp in historic_data:
        external_text.insert(tk.END, f"Hora: {timestamp}\nPrecio: {price} COP\nAerolínea: {airline}\n{'-'*40}\n")
    external_text.config(state=tk.DISABLED)  # Deshabilitar el widget de texto para evitar ediciones accidentales

def calcular_mejor_precio():
    """Calcula y muestra a qué hora el vuelo estuvo más económico."""
    if historic_data:
        min_price, min_airline, min_timestamp = min(historic_data, key=lambda x: x[0])
        messagebox.showinfo("Mejor Precio", f"El vuelo más económico fue a las {min_timestamp} con un precio de {min_price} COP y aerolínea {min_airline}.")
    else:
        messagebox.showinfo("Mejor Precio", "No hay datos disponibles para calcular el mejor precio.")

# Crear la interfaz gráfica con Tkinter
root = tk.Tk()
root.title("Buscador de Vuelos")

# Variables de los menús desplegables
departure_var = tk.StringVar(value="BOG")
arrival_var = tk.StringVar(value="SMR")

# Fecha actual y fecha predeterminada para la fecha de regreso (un día después)
fecha_actual = datetime.now()
fecha_actual1 = fecha_actual + timedelta(days=6)
fecha_regreso_predeterminada = fecha_actual + timedelta(days=7)

# Entrada de datos
tk.Label(root, text="ID de Salida:").grid(row=0, column=0, padx=10, pady=5)
departure_menu = tk.OptionMenu(root, departure_var, "BOG", "CTG", "SMR", "BAQ")
departure_menu.grid(row=0, column=1, padx=10, pady=5)

tk.Label(root, text="ID de Llegada:").grid(row=1, column=0, padx=10, pady=5)
arrival_menu = tk.OptionMenu(root, arrival_var, "BOG", "CTG", "SMR", "BAQ")
arrival_menu.grid(row=1, column=1, padx=10, pady=5)

tk.Label(root, text="Fecha de Salida:").grid(row=2, column=0, padx=10, pady=5)
outbound_date_entry = DateEntry(root, date_pattern='yyyy-mm-dd', mindate=fecha_actual1)
outbound_date_entry.grid(row=2, column=1, padx=10, pady=5)

tk.Label(root, text="Fecha de Regreso:").grid(row=3, column=0, padx=10, pady=5)
return_date_entry = DateEntry(root, date_pattern='yyyy-mm-dd', mindate=fecha_regreso_predeterminada)
return_date_entry.set_date(fecha_regreso_predeterminada)
return_date_entry.grid(row=3, column=1, padx=10, pady=5)

# Botón de búsqueda
tk.Button(root, text="Buscar Vuelos", command=search_flights).grid(row=4, columnspan=2, pady=10)

# Área de resultados
result_text = tk.StringVar()
result_label = tk.Label(root, textvariable=result_text, justify="left", wraplength=400)
result_label.grid(row=5, columnspan=2, padx=10, pady=10)

external_window = Toplevel(root)
external_window.title("Datos Históricos de Vuelos")
external_text = Text(external_window, wrap="word", width=50, height=20)
external_text.pack(padx=10, pady=10)
external_text.config(state=tk.DISABLED)  # Deshabilitar al inicio

# Botón para calcular el mejor precio
calculate_button = Button(external_window, text="Calcular Mejor Precio", command=calcular_mejor_precio)
calculate_button.pack(pady=10)

# Iniciar la interfaz y la búsqueda automática
root.after(10000, search_flights)  # Comenzar la búsqueda después de 1 segundo
root.mainloop()
