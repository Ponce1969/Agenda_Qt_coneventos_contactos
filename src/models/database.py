import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import secrets

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
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS compras (
                    id INTEGER PRIMARY KEY,
                    nombre TEXT,
                    cantidad TEXT,
                    precio TEXT
                )
            """)
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS usuarios (
                    id INTEGER PRIMARY KEY,
                    username TEXT UNIQUE,
                    password TEXT,
                    email TEXT,
                    role TEXT
                )
            """)
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS password_resets (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER,
                    token TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

    def agregar_usuario(self, username, password, email, role):
        hashed_password = generate_password_hash(password)
        with self.conn:
            self.conn.execute("INSERT INTO usuarios (username, password, email, role) VALUES (?, ?, ?, ?)", (username, hashed_password, email, role))

    def verificar_usuario(self, username, password):
        with self.conn:
            user = self.conn.execute("SELECT * FROM usuarios WHERE username = ?", (username,)).fetchone()
            if user and check_password_hash(user[2], password):
                return user
            return None

    def generar_token_recuperacion(self, email):
        with self.conn:
            user = self.conn.execute("SELECT * FROM usuarios WHERE email = ?", (email,)).fetchone()
            if user:
                token = secrets.token_urlsafe()
                self.conn.execute("INSERT INTO password_resets (user_id, token) VALUES (?, ?)", (user[0], token))
                return token
            return None

    def verificar_token_recuperacion(self, token):
        with self.conn:
            reset = self.conn.execute("SELECT * FROM password_resets WHERE token = ?", (token,)).fetchone()
            if reset:
                return reset
            return None
    
    def hay_usuarios(self):
        with self.conn:
            result = self.conn.execute("SELECT COUNT(*) FROM usuarios").fetchone()
            return result[0] > 0


    def cambiar_contrasena(self, user_id, new_password):
        hashed_password = generate_password_hash(new_password)
        with self.conn:
            self.conn.execute("UPDATE usuarios SET password = ? WHERE id = ?", (hashed_password, user_id))

    def eliminar_usuario(self, user_id):
        with self.conn:
            self.conn.execute("DELETE FROM usuarios WHERE id = ?", (user_id,))

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
    
    def obtener_compras(self):
        with self.conn:
            return self.conn.execute("SELECT * FROM compras").fetchall()

    def agregar_compra(self, nombre, cantidad, precio):
        with self.conn:
            self.conn.execute("INSERT INTO compras (nombre, cantidad, precio) VALUES (?, ?, ?)", (nombre, cantidad, precio))

    def editar_compra(self, compra_id, nombre, cantidad, precio):
        with self.conn:
            self.conn.execute("UPDATE compras SET nombre = ?, cantidad = ?, precio = ? WHERE id = ?", (nombre, cantidad, precio, compra_id))

    def eliminar_compra(self, compra_id):
        with self.conn:
            self.conn.execute("DELETE FROM compras WHERE id = ?", (compra_id,))    
        
    def compra_duplicada(self, nombre):
        with self.conn:
            result = self.conn.execute("SELECT * FROM compras WHERE nombre = ?", (nombre,)).fetchone()
            return result is not None    


