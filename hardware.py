import RPi.GPIO as GPIO
from gpiozero import Button
from grove.adc import ADC
import time
import config

class HardwareManager:
    def __init__(self):
        # --- 1. CONFIGURACIÓN ACTUADORES ---
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        
        GPIO.setup(config.PIN_LED, GPIO.OUT)
        GPIO.setup(config.PIN_RELE, GPIO.OUT)
        GPIO.setup(config.PIN_SERVO, GPIO.OUT)
        
        GPIO.output(config.PIN_LED, GPIO.LOW)
        GPIO.output(config.PIN_RELE, GPIO.LOW)
        
        self.st_led = "APAGADO"
        self.st_rele = "INACTIVO"
        self.st_servo = "0 (Abierto)"
        
        self.servo_pwm = GPIO.PWM(config.PIN_SERVO, 50)
        self.servo_pwm.start(0)
        
        # --- 2. INICIALIZAR ADC ---
        try:
            self.adc = ADC()
        except Exception as e:
            print(f"[ERROR CRÍTICO] No se detecta el HAT I2C: {e}")
            self.adc = None

        # --- 3. SENSORES DIGITALES ---
        self.contador_viento = 0
        self.ultimo_tiempo_viento = 0
        try:
            self.sensor_viento = Button(config.PIN_ANEMOMETRO, pull_up=True)
            self.sensor_viento.when_pressed = self._callback_viento
        except Exception as e:
            print(f"[ERROR] Anemómetro: {e}")

        self.contador_lluvia = 0
        try:
            self.sensor_lluvia = Button(config.PIN_PLUVIOMETRO, pull_up=True)
            self.sensor_lluvia.when_pressed = self._callback_lluvia
        except Exception as e:
            print(f"[ERROR] Pluviómetro: {e}")

    # --- CALLBACKS ---
    def _callback_viento(self):
        ahora = time.time()
        if (ahora - self.ultimo_tiempo_viento) > 0.015:
            self.contador_viento += 1
            self.ultimo_tiempo_viento = ahora

    def _callback_lluvia(self):
        self.contador_lluvia += 1

    # --- LECTURA ---
    def obtener_datos_raw(self):
        v = self.contador_viento
        l = self.contador_lluvia
        self.contador_viento = 0
        self.contador_lluvia = 0 
        return v, l

    # --- VELETA ---
    def leer_veleta_datos(self):
        """Devuelve (nombre_direccion, resistencia_calculada)"""
        if self.adc is None: return "Error", 0
        
        # 1. Leer RAW y convertir a Voltaje 
        raw_value = self.adc.read(config.CANAL_VELETA)
        voltage = raw_value * config.VCC / config.ADC_MAX
        
        # 2. Calcular Resistencia
        if voltage >= config.VCC - 0.01:
            r_veleta = 999999
        elif voltage <= 0.01:
            r_veleta = 0
        else:
            r_veleta = (config.R_EXT * voltage) / (config.VCC - voltage)

        # 3. Buscar Dirección 
        closest_direction = "Desconocido"
        min_diff = 999999.0

        for val, direction in config.DIRECTION_MAP:
            diff = abs(r_veleta - val)
            if diff < min_diff:
                min_diff = diff
                closest_direction = direction
        
        return closest_direction, int(r_veleta)

    def leer_luz(self):
        if self.adc is None: return 0
        return self.adc.read(config.CANAL_LUZ)

    # --- CONTROL ---
    def controlar_servo(self, angulo):
        self.st_servo = f"{angulo}"
        duty = 2.5 + (angulo / 18.0)
        self.servo_pwm.ChangeDutyCycle(duty)
        time.sleep(0.3)
        self.servo_pwm.ChangeDutyCycle(0)

    def controlar_led(self, encendido):
        estado = GPIO.HIGH if encendido else GPIO.LOW
        GPIO.output(config.PIN_LED, estado)
        self.st_led = "ON" if encendido else "OFF"

    def controlar_rele(self, activado):
        estado = GPIO.HIGH if activado else GPIO.LOW
        GPIO.output(config.PIN_RELE, estado)
        self.st_rele = "ON" if activado else "OFF"

    def obtener_estados(self):
        return self.st_led, self.st_rele, self.st_servo

    def limpiar(self):
        try:
            self.servo_pwm.stop()
            self.sensor_viento.close()
            self.sensor_lluvia.close()
            GPIO.cleanup()
        except:
            pass