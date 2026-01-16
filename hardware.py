import RPi.GPIO as GPIO
import smbus2
import time
import config

class HardwareManager:
    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        
        # Configurar Entradas Digitales
        GPIO.setup(config.PIN_ANEMOMETRO, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(config.PIN_PLUVIOMETRO, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        
        # Configurar Salidas Digitales
        GPIO.setup(config.PIN_LED, GPIO.OUT)
        GPIO.setup(config.PIN_RELE, GPIO.OUT)
        GPIO.setup(config.PIN_SERVO, GPIO.OUT)
        
        # Configurar PWM para Servo (50Hz estándar)
        self.servo_pwm = GPIO.PWM(config.PIN_SERVO, 50)
        self.servo_pwm.start(0)
        
        # Configurar I2C para Analógicos
        self.bus = smbus2.SMBus(1)
        
        # Variables para contadores de interrupciones
        self.pulsos_viento = 0
        self.pulsos_lluvia = 0
        
        # Activar interrupciones (Eventos)
        GPIO.add_event_detect(config.PIN_ANEMOMETRO, GPIO.FALLING, callback=self._contar_viento, bouncetime=50)
        GPIO.add_event_detect(config.PIN_PLUVIOMETRO, GPIO.FALLING, callback=self._contar_lluvia, bouncetime=200)

    # --- Callbacks de Interrupción ---
    def _contar_viento(self, channel):
        self.pulsos_viento += 1

    def _contar_lluvia(self, channel):
        self.pulsos_lluvia += 1

    # --- Lectura de Sensores ---
    def obtener_pulsos_y_resetear(self):
        """Devuelve los pulsos acumulados y reinicia contadores"""
        v = self.pulsos_viento
        l = self.pulsos_lluvia
        self.pulsos_viento = 0
        self.pulsos_lluvia = 0
        return v, l

    def leer_adc(self, canal):
        """Lee valor crudo (0-4095) del Grove Base Hat via I2C"""
        try:
            # Comando para leer del registro del ADC en el Hat
            self.bus.write_byte_data(config.I2C_ADDR_ADC, 0x10 | canal, 0)
            time.sleep(0.05) # Espera conversión
            data = self.bus.read_i2c_block_data(config.I2C_ADDR_ADC, 0x10 | canal, 2)
            val = data[0] | (data[1] << 8) # Unir bytes
            return val
        except Exception as e:
            print(f"Error I2C: {e}")
            return 0

    def leer_veleta(self):
        val = self.leer_adc(config.CANAL_VELETA)
        # Convertir voltaje a grados aprox (simplificado)
        return int((val / 4095.0) * 360)

    def leer_luz(self):
        return self.leer_adc(config.CANAL_LUZ)

    # --- Control de Actuadores ---
    def controlar_servo(self, angulo):
        # Conversión de ángulo a Duty Cycle (2.5% a 12.5%)
        duty = 2.5 + (angulo / 18.0)
        self.servo_pwm.ChangeDutyCycle(duty)
        time.sleep(0.3) # Dar tiempo a moverse
        self.servo_pwm.ChangeDutyCycle(0) # Detener vibración

    def controlar_led(self, estado):
        # estado: 0=Apagado, 1=Encendido, 2=Parpadeo (gestionado en main)
        GPIO.output(config.PIN_LED, estado)

    def controlar_rele(self, estado):
        GPIO.output(config.PIN_RELE, estado)

    def limpiar(self):
        self.servo_pwm.stop()
        GPIO.cleanup()