import sqlite3
import mysql.connector
import config
from datetime import datetime, timedelta

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
        cursor_remoto = None
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

            ids_subidos = []
            for fila in filas:
                val = (fila[1], fila[2], fila[3], fila[4], fila[5], fila[6])
                cursor_remoto.execute(sql_insert, val)
                ids_subidos.append((fila[0],))

            conn_remota.commit()

            self.cursor_local.executemany(
                'UPDATE mediciones SET sincronizado = 1 WHERE id = ?',
                ids_subidos
            )
            self.conn_local.commit()

            for (id_local,) in ids_subidos:
                print(f"[NUBE] Dato ID {id_local} subido a MySQL.")

            self.borrar_local_sincronizado_antiguo()

        except mysql.connector.Error as err:
            if conn_remota:
                try:
                    conn_remota.rollback()
                except:
                    pass
            print(f"[ERROR NUBE] MySQL Error: {err}")
        finally:
            if cursor_remoto:
                try:
                    cursor_remoto.close()
                except:
                    pass
            if conn_remota and conn_remota.is_connected():
                conn_remota.close()

    def borrar_local_sincronizado_antiguo(self, minutos=None):
        if minutos is None:
            minutos = getattr(config, "RETENCION_LOCAL_MINUTOS", 5)

        cutoff = (datetime.now() - timedelta(minutes=minutos)).strftime("%Y-%m-%d %H:%M:%S")
        self.cursor_local.execute(
            "DELETE FROM mediciones WHERE sincronizado = 1 AND fecha < ?",
            (cutoff,)
        )
        borrados = self.cursor_local.rowcount
        self.conn_local.commit()

        if borrados and borrados > 0:
            print(f"[LOCAL] Borradas {borrados} filas sincronizadas anteriores a {cutoff}.")

    def cerrar(self):
        self.conn_local.close()