import sqlite3
import requests
import config
from datetime import datetime

class DataManager:
    def __init__(self):
        self.conn = sqlite3.connect(config.DB_NAME)
        self.cursor = self.conn.cursor()
        self.crear_tabla()

    def crear_tabla(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS mediciones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha TEXT,
                viento INTEGER,
                lluvia INTEGER,
                luz INTEGER,
                direccion INTEGER,
                estado_sistema TEXT,
                sincronizado INTEGER DEFAULT 0
            )
        ''')
        self.conn.commit()

    def guardar_dato(self, datos):
        """Guarda datos en local"""
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute('''
            INSERT INTO mediciones (fecha, viento, lluvia, luz, direccion, estado_sistema)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (fecha, datos['viento'], datos['lluvia'], datos['luz'], datos['direccion'], datos['estado']))
        self.conn.commit()
        print(f"[DB] Dato guardado localmente: {fecha}")

    def sincronizar_nube(self):
        """Sube datos no sincronizados a Clever Cloud"""
        # Seleccionar datos no enviados (sincronizado = 0)
        self.cursor.execute('SELECT * FROM mediciones WHERE sincronizado = 0')
        filas = self.cursor.fetchall()

        if not filas:
            return

        for fila in filas:
            payload = {
                "id": fila[0], "fecha": fila[1], "viento": fila[2],
                "lluvia": fila[3], "luz": fila[4], "direccion": fila[5],
                "estado": fila[6]
            }
            try:
                # Envio HTTP POST
                # response = requests.post(config.CLOUD_URL, json=payload, timeout=2)
                # if response.status_code == 200:
                
                # SIMULACIÓN DE ÉXITO (Descomentar líneas de arriba con URL real)
                print(f"[CLOUD] Dato ID {fila[0]} enviado a la nube.")
                
                # Marcar como enviado o borrar (según diagrama cite: 2179)
                self.cursor.execute('UPDATE mediciones SET sincronizado = 1 WHERE id = ?', (fila[0],))
                # Opcional: self.cursor.execute('DELETE FROM mediciones WHERE id = ?', (fila[0],))
                
            except Exception as e:
                print(f"[CLOUD] Error de conexión: {e}")
                break # Si falla uno, parar para reintentar luego
        
        self.conn.commit()

    def cerrar(self):
        self.conn.close()