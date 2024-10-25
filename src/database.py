import sqlite3
from contextlib import contextmanager
from datetime import datetime

class Database:
    def __init__(self, db_name):
        self.db_name = db_name
        self._create_table()

    def _create_table(self):
        """Crea la tabla de eventos si no existe."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS eventos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fecha_hora DATETIME NOT NULL,
                    descripcion TEXT NOT NULL
                )
            ''')
            conn.commit()

    @contextmanager
    def _get_connection(self):
        """Context manager para obtener una conexión a la base de datos."""
        conn = sqlite3.connect(self.db_name)
        try:
            yield conn
        finally:
            conn.close()

    def agregar_evento(self, fecha, hora, descripcion):
        """Agrega un nuevo evento a la base de datos."""
        fecha_hora_str = f"{fecha} {hora}"
        try:
            # Convertir la cadena de fecha y hora a un objeto datetime
            fecha_hora = datetime.strptime(fecha_hora_str, '%Y-%m-%d %H:%M')
        except ValueError:
            raise ValueError("Formato de fecha u hora incorrecto. Use 'YYYY-MM-DD' para la fecha y 'HH:MM' para la hora.")

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO eventos (fecha_hora, descripcion)
                VALUES (?, ?)
            ''', (fecha_hora, descripcion))
            conn.commit()

    def obtener_eventos(self):
        """Obtiene todos los eventos de la base de datos."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id, fecha_hora, descripcion FROM eventos')
            return cursor.fetchall()

    def editar_evento_completo(self, evento_id, nueva_fecha_hora, nueva_descripcion):
        """Edita la fecha, hora y descripción de un evento existente."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE eventos
                SET fecha_hora = ?, descripcion = ?
                WHERE id = ?
            ''', (nueva_fecha_hora, nueva_descripcion, evento_id))
            conn.commit()

    def eliminar_evento(self, evento_id):
        """Elimina un evento de la base de datos."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                DELETE FROM eventos
                WHERE id = ?
            ''', (evento_id,))
            conn.commit()

    
        
        
        




