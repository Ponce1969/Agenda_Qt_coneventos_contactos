import sqlite3

class Database:
    def __init__(self, db_path):
        self.conn = sqlite3.connect(db_path)
        self.create_tables()

    def create_tables(self):
        with self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS eventos (
                    id INTEGER PRIMARY KEY,
                    fecha_hora TEXT,
                    descripcion TEXT
                )
            """)
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS contactos (
                    id INTEGER PRIMARY KEY,
                    nombre TEXT,
                    telefono TEXT,
                    email TEXT,
                    documento TEXT
                )
            """)

    def obtener_eventos(self):
        with self.conn:
            return self.conn.execute("SELECT * FROM eventos").fetchall()

    def agregar_evento(self, fecha, hora, descripcion):
        with self.conn:
            self.conn.execute("INSERT INTO eventos (fecha_hora, descripcion) VALUES (?, ?)", (f"{fecha} {hora}", descripcion))

    def editar_evento_completo(self, evento_id, nueva_fecha_hora, nueva_descripcion):
        with self.conn:
            self.conn.execute("UPDATE eventos SET fecha_hora = ?, descripcion = ? WHERE id = ?", (nueva_fecha_hora, nueva_descripcion, evento_id))

    def eliminar_evento(self, evento_id):
        with self.conn:
            self.conn.execute("DELETE FROM eventos WHERE id = ?", (evento_id,))

    def obtener_contactos(self):
        with self.conn:
            return self.conn.execute("SELECT * FROM contactos").fetchall()

    def agregar_contacto(self, nombre, telefono, email, documento):
        with self.conn:
            self.conn.execute("INSERT INTO contactos (nombre, telefono, email, documento) VALUES (?, ?, ?, ?)", (nombre, telefono, email, documento))

    def editar_contacto(self, contacto_id, nombre, telefono, email, documento):
        with self.conn:
            self.conn.execute("UPDATE contactos SET nombre = ?, telefono = ?, email = ?, documento = ? WHERE id = ?", (nombre, telefono, email, documento, contacto_id))

    def eliminar_contacto(self, contacto_id):
        with self.conn:
            self.conn.execute("DELETE FROM contactos WHERE id = ?", (contacto_id,))
     
    def contacto_duplicado(self, email, documento):
        with self.conn:
            result = self.conn.execute("SELECT * FROM contactos WHERE email = ? OR documento = ?", (email, documento)).fetchone()
            return result is not None
    
        
        
        




