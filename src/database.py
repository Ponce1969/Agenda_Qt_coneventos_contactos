import sqlite3
from contextlib import contextmanager

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
                    fecha TEXT NOT NULL,
                    hora TEXT NOT NULL,
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
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO eventos (fecha, hora, descripcion)
                VALUES (?, ?, ?)
            ''', (fecha, hora, descripcion))
            conn.commit()

    def obtener_eventos(self):
        """Obtiene todos los eventos de la base de datos."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM eventos')
            return cursor.fetchall()

    def editar_evento(self, evento_id, nueva_descripcion):
        """Edita la descripción de un evento existente."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE eventos
                SET descripcion = ?
                WHERE id = ?
            ''', (nueva_descripcion, evento_id))
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

   
    
        
        
        




