import sqlite3
import mysql.connector
import config
from datetime import datetime

class DataManager:
    def __init__(self):
        # Conexión Local (SQLite)
        self.conn_local = sqlite3.connect(config.DB_LOCAL)
        self.cursor_local = self.conn_local.cursor()
        self.crear_tabla_local()

    def crear_tabla_local(self):
        self.cursor_local.execute('''
            CREATE TABLE IF NOT EXISTS mediciones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha TEXT,
                viento INTEGER,
                lluvia INTEGER,
                luz INTEGER,
                direccion TEXT,  
                estado_sistema TEXT,
                sincronizado INTEGER DEFAULT 0
            )
        ''')
        self.conn_local.commit()

    def guardar_dato(self, datos):
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cursor_local.execute('''
            INSERT INTO mediciones (fecha, viento, lluvia, luz, direccion, estado_sistema)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (fecha, datos['viento'], datos['lluvia'], datos['luz'], datos['direccion'], datos['estado']))
        self.conn_local.commit()
        print(f"[LOCAL] Dato guardado: {fecha}")

    def sincronizar_nube(self):
        self.cursor_local.execute('SELECT * FROM mediciones WHERE sincronizado = 0')
        filas = self.cursor_local.fetchall()

        if not filas:
            return 

        conn_remota = None
        try:
            conn_remota = mysql.connector.connect(
                host=config.MYSQL_HOST,
                port=config.MYSQL_PORT,
                user=config.MYSQL_USER,
                password=config.MYSQL_PASSWORD,
                database=config.MYSQL_DB,
                connect_timeout=5
            )
            cursor_remoto = conn_remota.cursor()

            cursor_remoto.execute('''
                CREATE TABLE IF NOT EXISTS mediciones (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    fecha VARCHAR(50),
                    viento INT,
                    lluvia INT,
                    luz INT,
                    direccion VARCHAR(20),
                    estado VARCHAR(50)
                )
            ''')

            sql_insert = "INSERT INTO mediciones (fecha, viento, lluvia, luz, direccion, estado) VALUES (%s, %s, %s, %s, %s, %s)"
            
            for fila in filas:
                # fila = (id, fecha, viento, lluvia, luz, direccion, estado, sinc)
                val = (fila[1], fila[2], fila[3], fila[4], fila[5], fila[6])
                cursor_remoto.execute(sql_insert, val)
                
                self.cursor_local.execute('UPDATE mediciones SET sincronizado = 1 WHERE id = ?', (fila[0],))
                print(f"[NUBE] Dato ID {fila[0]} subido a MySQL.")

            conn_remota.commit()
            self.conn_local.commit()

        except mysql.connector.Error as err:
            print(f"[ERROR NUBE] MySQL Error: {err}")
        finally:
            if conn_remota and conn_remota.is_connected():
                cursor_remoto.close()
                conn_remota.close()

    def cerrar(self):
        self.conn_local.close()