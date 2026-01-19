import sqlite3
import requests
import json
import os
from datetime import datetime, timedelta, timezone

# --- CONFIGURACIÓN ---
API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjaSI6MTY0MjQwOTcsImlhdCI6MTc2ODE3OTg2MX0.sGgRNVqwemVcJH0vZPyDKdL3rUbf2CNb0HVw9OJfjnY"
STATION_ID = 0  
URL = f"https://stations.windy.com/pws/update/{API_KEY}"

# Ruta dinámica a la base de datos
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'meteorologia.db')

# Mapa inverso para convertir tu texto a Grados
DIRECCIONES_GRADOS = {
    "Norte": 0, "Noreste": 45, "Este": 90, "Sureste": 135,
    "Sur": 180, "Suroeste": 225, "Oeste": 270, "Noroeste": 315,
    "Desconocido": 0
}

def obtener_ultimo_dato():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT viento, lluvia, luz, fecha, direccion FROM mediciones ORDER BY id DESC LIMIT 1")
        dato = cursor.fetchone()
        conn.close()
        return dato
    except Exception as e:
        print(f"Error leyendo la base de datos: {e}")
        return None

def convertir_a_utc(fecha_str_local):
    """Convierte string de hora local (Pi) a string de hora UTC (Windy)"""
    try:
        # 1. Convertir el string de la DB a objeto datetime
        dt_local = datetime.strptime(fecha_str_local, "%Y-%m-%d %H:%M:%S")
        
        # 2. Hacer que el objeto sepa que es 'hora local' del sistema
        # (astimezone() sin argumentos usa la zona horaria de la Raspberry)
        dt_aware = dt_local.astimezone() 
        
        # 3. Convertir a UTC
        dt_utc = dt_aware.astimezone(timezone.utc)
        
        # 4. Devolver en formato string limpio
        return dt_utc.strftime("%Y-%m-%d %H:%M:%S")
    except Exception as e:
        print(f"Error convirtiendo fecha: {e}. Usando hora actual UTC.")
        return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

def subir_datos_windy():
    print("--- Intentando subir datos a Windy ---")
    
    dato = obtener_ultimo_dato()

    if dato:
        viento_kmh = dato[0]
        lluvia_mm = dato[1]
        luz = dato[2]       
        fecha_str_local = dato[3] # Esto está en hora española
        dir_texto = dato[4] 

        # --- CONVERSIONES ---
        # 1. Velocidad: km/h a m/s
        wind_ms = viento_kmh / 3.6
        
        # 2. Dirección: Texto a Grados
        wind_dir = DIRECCIONES_GRADOS.get(dir_texto, 0)

        # 3. Fecha: Local a UTC (CRÍTICO PARA QUE WINDY ACEPTE)
        fecha_utc = convertir_a_utc(fecha_str_local)

        payload = {
            "observations": [{
                "station": STATION_ID,
                "wind": round(wind_ms, 2),
                "winddir": wind_dir,
                "rain": lluvia_mm,
                "dateutc": fecha_utc  # Enviamos la hora corregida
            }]
        }

        print(f"Datos a enviar (UTC): {payload}")

        try:
            response = requests.post(URL, json=payload, timeout=10)
            
            if response.status_code == 200:
                print("Datos aceptados por Windy.")
            else:
                print(f"ERROR Windy: Código {response.status_code}")
                print(response.text)
                
        except requests.exceptions.RequestException as e:
            print(f"Error de conexion: {e}")
    else:
        print("No se encontraron datos en la base de datos local.")

if __name__ == "__main__":
    subir_datos_windy()