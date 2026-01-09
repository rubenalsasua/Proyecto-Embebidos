import RPi.GPIO as GPIO
import time

# Configuracion del puerto
# Se utiliza el puerto D22 del Grove HAT
PIN = 22
FACTOR = 2.4  # Factor de conversion: 1 Hz = 2.4 km/h

# Variables para la cuenta de vueltas
contador = 0
ultimo_tiempo = 0

# Iniciamos la placa y configuramos el GPIO
GPIO.setmode(GPIO.BCM)
# Activamos resistencia Pull-Up interna
GPIO.setup(PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Funcion que se ejecuta automaticamente al detectar movimiento
def contar(channel):
    global contador, ultimo_tiempo
    
    # Filtro de seguridad para evitar rebotes (ruido)
    # Solo cuenta si han pasado mas de 15ms desde el ultimo pulso
    ahora = time.time()
    if (ahora - ultimo_tiempo) > 0.015:
        contador = contador + 1
        ultimo_tiempo = ahora

# Activamos la escucha en el pin 22 (flanco de bajada)
try:
    GPIO.add_event_detect(PIN, GPIO.FALLING, callback=contar, bouncetime=50)
except:
    print("Error activando el GPIO")

print("--- Leyendo Anemometro (Puerto D22) ---")

try:
    while True:
        # Guardamos pulsos actuales y reiniciamos contador
        pulsos_actuales = contador
        contador = 0
        
        # Esperamos 1 segundo exacto para el calculo de frecuencia
        time.sleep(1)
        
        # Calculo de velocidad: Pulsos/segundo * Factor
        velocidad = pulsos_actuales * FACTOR
        
        print(f"Velocidad: {velocidad:.2f} kph")

except KeyboardInterrupt:
    print("\nSaliendo...")
    GPIO.cleanup()
