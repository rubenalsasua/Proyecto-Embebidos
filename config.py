# --- PINES DEL GROVE BASE HAT ---
PIN_ANEMOMETRO = 16      # D16 (Digital)
PIN_PLUVIOMETRO = 17     # D17 (Digital)
PIN_LED = 18             # D18 (Digital)
PIN_RELE = 19            # D19 (Digital)
PIN_SERVO = 12           # PWM Port (GPIO 12 es hardware PWM en Pi)

# Direccion I2C para sensores analógicos (Base Hat)
I2C_ADDR_ADC = 0x04      
CANAL_VELETA = 0         # A0
CANAL_LUZ = 1            # A1

# --- UMBRALES DE ALERTA [cite: 2152-2155] ---
# Umbrales de Viento (pulsos por intervalo de 5s)
VIENTO_UMBRAL_AVISO = 5
VIENTO_UMBRAL_EMERGENCIA = 15

# Umbrales de Lluvia (pulsos por intervalo de 5s)
LLUVIA_UMBRAL_AVISO = 1
LLUVIA_UMBRAL_EMERGENCIA = 5

# --- BASE DE DATOS Y CLOUD ---
DB_NAME = "/home/pi/proyecto_embebidos/meteorologia.db"
CLOUD_URL = "https://user_f73dcfa7-2c97-4200-b112-622a5836f72e-cloud.com/api/v1/datos"