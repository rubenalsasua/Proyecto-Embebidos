# --- PINES DIGITALES ---
PIN_ANEMOMETRO = 22      # gpiozero
PIN_PLUVIOMETRO = 5      # gpiozero
PIN_LED = 18             # RPi.GPIO
PIN_RELE = 24            # RPi.GPIO
PIN_SERVO = 12           # PWM

# --- CANALES ANALÓGICOS (ADC) ---
CANAL_VELETA = 0         # A0
CANAL_LUZ = 2            # A2

# --- PARÁMETROS ELÉCTRICOS ---
VCC = 3.3   
R_EXT = 10000.0
ADC_MAX = 4095.0


DIRECTION_MAP = [
    (160,  "Noreste"),
    (200,  "Norte"),
    (310,  "Este"),
    (620,  "Sureste"),
    (1700, "Sur"),
    (2020, "Oeste"),
    (2310, "Noroeste"),
    (2460, "Suroeste")
]

# --- FACTORES DE CONVERSIÓN ---
FACTOR_VIENTO = 2.4      
MM_POR_VUELCO = 0.2794   

# --- UMBRALES ---
VIENTO_UMBRAL_AVISO = 40       
VIENTO_UMBRAL_EMERGENCIA = 70  
LLUVIA_UMBRAL_AVISO = 2        
LLUVIA_UMBRAL_EMERGENCIA = 10  

# --- DATOS ---
DB_LOCAL = "/home/deusto/Proyecto-Embebidos/Proyecto-Embebidos/meteorologia.db"
MYSQL_HOST = "bbb7f5pmlzbofierkupo-mysql.services.clever-cloud.com"
MYSQL_PORT = 3306
MYSQL_USER = "uftt9g8twsyhyigc"
MYSQL_PASSWORD = "MxdtVEZvjcBKdDD3dGki"
MYSQL_DB = "bbb7f5pmlzbofierkupo"

# --- FILTRADO VELETA ---
VELETA_MUESTRAS = 7
VELETA_DELAY_MUESTRA = 0.005

# --- RETENCIÓN LOCAL ---
RETENCION_LOCAL_MINUTOS = 5