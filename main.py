import time
import config
from hardware import HardwareManager
from data_manager import DataManager

def main():
    print("--- INICIANDO ESTACIÓN METEOROLÓGICA (Grupo 10) ---")
    
    # Inicializar módulos
    hw = HardwareManager()
    db = DataManager()
    
    # Variables de control
    estado_actual = "NORMAL"
    led_blink_state = False
    
    try:
        while True:
            # 1. ADQUISICIÓN (Muestreo cada 5 segundos)
            time.sleep(5) 
            
            # Obtener datos brutos
            pulsos_viento, pulsos_lluvia = hw.obtener_pulsos_y_resetear()
            nivel_luz = hw.leer_luz()
            direccion_viento = hw.leer_veleta()
            
            print(f"Lectura -> Viento: {pulsos_viento} | Lluvia: {pulsos_lluvia} | Luz: {nivel_luz}")

            # 2. LÓGICA DE ESTADOS (Automatización) 
            
            # --- ESTADO EMERGENCIA ---
            if pulsos_viento > config.VIENTO_UMBRAL_EMERGENCIA or pulsos_lluvia > config.LLUVIA_UMBRAL_EMERGENCIA:
                estado_actual = "EMERGENCIA"
                # Actuadores: LED Fijo, Servo 180 (Cerrado), Relé ON
                hw.controlar_led(1)
                hw.controlar_servo(180)
                hw.controlar_rele(1)
                print("!!! ALERTA: EMERGENCIA ACTIVADA !!!")

            # --- ESTADO AVISO ---
            elif pulsos_viento > config.VIENTO_UMBRAL_AVISO or pulsos_lluvia >= config.LLUVIA_UMBRAL_AVISO:
                estado_actual = "AVISO"
                # Actuadores: LED Parpadea, Servo 45 (Medio), Relé OFF
                led_blink_state = not led_blink_state # Alternar estado
                hw.controlar_led(led_blink_state)
                hw.controlar_servo(45)
                hw.controlar_rele(0)
                print("! ALERTA: AVISO")

            # --- ESTADO NORMAL ---
            else:
                estado_actual = "NORMAL"
                # Actuadores: LED Off, Servo 0 (Abierto), Relé OFF
                hw.controlar_led(0)
                hw.controlar_servo(0)
                hw.controlar_rele(0)

            # 3. PERSISTENCIA Y NUBE [cite: 2166-2172]
            datos_para_guardar = {
                "viento": pulsos_viento,
                "lluvia": pulsos_lluvia,
                "luz": nivel_luz,
                "direccion": direccion_viento,
                "estado": estado_actual
            }
            
            db.guardar_dato(datos_para_guardar)
            db.sincronizar_nube()

    except KeyboardInterrupt:
        print("Deteniendo sistema...")
    finally:
        hw.limpiar()
        db.cerrar()

if __name__ == "__main__":
    main()