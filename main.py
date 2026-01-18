import time
import config
from hardware import HardwareManager
from data_manager import DataManager

def main():
    print("\n" + "="*60)
    print("   INICIANDO SISTEMA DE MONITORIZACION (V3.1 Veleta OK)")
    print("="*60)
    
    try:
        hw = HardwareManager()
        db = DataManager()
    except Exception as e:
        print(f"[FATAL] Error inicializando: {e}")
        return
    
    estado_actual = "NORMAL"
    led_blink = False
    INTERVALO = 5 
    
    try:
        while True:
            # Barra de progreso visual
            for _ in range(INTERVALO):
                time.sleep(1)
                print(".", end="", flush=True)
            print() 
            
            # --- 1. LECTURA ---
            pulsos_v, pulsos_l = hw.obtener_datos_raw()
            luz = hw.leer_luz()
            
            # Leemos ángulo (texto) y resistencia (int)
            nombre_direccion, resistencia_calc = hw.leer_veleta_datos()
            
            # Matemáticas
            vel_kmh = (pulsos_v / INTERVALO) * config.FACTOR_VIENTO
            lluvia_mm = pulsos_l * config.MM_POR_VUELCO
            
            # --- 2. LOGICA ---
            if vel_kmh > config.VIENTO_UMBRAL_EMERGENCIA or lluvia_mm > config.LLUVIA_UMBRAL_EMERGENCIA:
                estado_actual = "3 - EMERGENCIA"
                hw.controlar_led(True)
                hw.controlar_servo(180)
                hw.controlar_rele(True)

            elif vel_kmh > config.VIENTO_UMBRAL_AVISO or lluvia_mm >= config.LLUVIA_UMBRAL_AVISO:
                estado_actual = "2 - ALERTA"
                led_blink = not led_blink
                hw.controlar_led(led_blink)
                hw.controlar_servo(45)
                hw.controlar_rele(False)

            else:
                estado_actual = "1 - NORMAL"
                hw.controlar_led(False)
                hw.controlar_servo(0)
                hw.controlar_rele(False)

            # --- 3. MOSTRAR PANEL ---
            st_led, st_rele, st_servo = hw.obtener_estados()
            
            print("\n" + "+" + "-"*58 + "+")
            print(f"|  ESTADO: {estado_actual:^47} |")
            print("+" + "-"*58 + "+")
            print(f"|  VIENTO:   {vel_kmh:6.2f} km/h  ({pulsos_v:3} pulsos)      |")
            print(f"|  LLUVIA:   {lluvia_mm:6.2f} mm    ({pulsos_l:3} vuelcos)     |")
            print(f"|  LUZ:      {luz:<6}                              |")
            print(f"|  VELETA:   {nombre_direccion:^12}    |")
            print("+" + "-"*58 + "+")
            print(f"|  ACTUADORES: LED={st_led:<3} | RELE={st_rele:<3} | SERVO={st_servo} |")
            print("+" + "-"*58 + "+")

            # --- 4. PERSISTENCIA ---
            datos = {
                "viento": vel_kmh, 
                "lluvia": lluvia_mm,
                "luz": luz, 
                "direccion": nombre_direccion,
                "estado": estado_actual
            }
            db.guardar_dato(datos)
            db.sincronizar_nube()

    except KeyboardInterrupt:
        print("\n[STOP] Deteniendo sistema...")
    finally:
        hw.limpiar()
        db.cerrar()

if __name__ == "__main__":
    main()