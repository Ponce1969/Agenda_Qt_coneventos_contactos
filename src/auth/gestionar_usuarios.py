from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, 
    QTableWidget, QTableWidgetItem, QMessageBox, QInputDialog, QComboBox
)
from models.database import Database
import time

class GestionarUsuariosWindow(QDialog):
    def __init__(self, db: Database, rol_usuario: str):
        super().__init__()
        self.db = db
        self.rol_usuario = rol_usuario  # Almacena el rol del usuario logeado
        self.usuarios = []  # Lista para almacenar los usuarios
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Gestionar Usuarios")
        self.setGeometry(150, 150, 600, 400)
        
        self.layout = QVBoxLayout()
        
        # Tabla de usuarios
        self.tabla_usuarios = QTableWidget()
        self.tabla_usuarios.setColumnCount(3)  # Solo mostrar username, email y role
        self.tabla_usuarios.setHorizontalHeaderLabels(["Username", "Email", "Role"])
        self.tabla_usuarios.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla_usuarios.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.layout.addWidget(self.tabla_usuarios)

        # Botones para agregar y eliminar usuarios
        self.btn_agregar = QPushButton("Agregar Usuario")
        self.btn_agregar.clicked.connect(self.agregar_usuario)
        self.layout.addWidget(self.btn_agregar)

        self.btn_eliminar = QPushButton("Eliminar Usuario")
        self.btn_eliminar.clicked.connect(self.eliminar_usuario)
        self.layout.addWidget(self.btn_eliminar)

        self.setLayout(self.layout)
        self.cargar_usuarios()

    def tiene_permiso(self):
        """Verifica si el usuario actual tiene permisos de administrador"""
        if self.rol_usuario != "admin":
            QMessageBox.warning(self, "Acceso Denegado", "Solo los administradores pueden realizar esta acción.")
            return False
        return True

    def cargar_usuarios(self):
        """Carga los usuarios desde la base de datos"""
        self.usuarios = self.db.obtener_usuarios()
        self.tabla_usuarios.setRowCount(0)
        for usuario in self.usuarios:
            row_position = self.tabla_usuarios.rowCount()
            self.tabla_usuarios.insertRow(row_position)
            self.tabla_usuarios.setItem(row_position, 0, QTableWidgetItem(usuario[1]))  # username
            self.tabla_usuarios.setItem(row_position, 1, QTableWidgetItem(usuario[2]))  # email
            self.tabla_usuarios.setItem(row_position, 2, QTableWidgetItem(usuario[3]))  # role

    def agregar_usuario(self):
        """Agrega un nuevo usuario"""
        if not self.tiene_permiso():
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("Agregar Usuario")
        dialog.setGeometry(150, 150, 300, 200)
        
        layout = QVBoxLayout(dialog)
        
        username_label = QLabel("Nombre de usuario:")
        username_input = QLineEdit()
        layout.addWidget(username_label)
        layout.addWidget(username_input)
        
        password_label = QLabel("Contraseña:")
        password_input = QLineEdit()
        password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(password_label)
        layout.addWidget(password_input)
        
        email_label = QLabel("Correo electrónico:")
        email_input = QLineEdit()
        layout.addWidget(email_label)
        layout.addWidget(email_input)
        
        role_label = QLabel("Rol:")
        role_input = QComboBox()
        role_input.addItems(["admin", "ayudante"])
        layout.addWidget(role_label)
        layout.addWidget(role_input)
        
        btn_guardar = QPushButton("Guardar")
        btn_guardar.clicked.connect(lambda: self.guardar_usuario(dialog, username_input, password_input, email_input, role_input))
        layout.addWidget(btn_guardar)
        
        dialog.setLayout(layout)
        dialog.exec()

    def guardar_usuario(self, dialog, username_input, password_input, email_input, role_input):
        """Guarda un nuevo usuario en la base de datos"""
        username = username_input.text()
        password = password_input.text()
        email = email_input.text()
        role = role_input.currentText()
        
        if not username or not password or not email:
            QMessageBox.warning(self, "Error", "Todos los campos son obligatorios")
            return
        
        try:
            self.db.agregar_usuario(username, password, email, role)
            QMessageBox.information(self, "Éxito", "Usuario agregado correctamente")
            self.cargar_usuarios()
            dialog.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Ocurrió un error al agregar el usuario: {str(e)}")

    def eliminar_usuario(self):
        """Elimina un usuario seleccionado"""
        if not self.tiene_permiso():
            return

        selected_row = self.tabla_usuarios.currentRow()
        if selected_row >= 0:
            user_id = self.usuarios[selected_row][0]  # Obtener el ID del usuario desde la lista de usuarios
            
            respuesta = QMessageBox.question(
                self, "Confirmación",
                "¿Estás seguro de que deseas eliminar este usuario?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if respuesta == QMessageBox.StandardButton.Yes:
                # Solicitar la contraseña del administrador
                admin_password, ok = QInputDialog.getText(self, "Confirmación de Administrador", "Ingresa la contraseña del administrador:", QLineEdit.EchoMode.Password)
                if not ok or not admin_password:
                    return

                # Verificar la contraseña del administrador
                if not self.db.verificar_contrasena_admin(admin_password):
                    QMessageBox.warning(self, "Error", "Contraseña de administrador incorrecta.")
                    return

                try:
                    self.db.eliminar_usuario(user_id)
                    self.cargar_usuarios()
                    QMessageBox.information(self, "Éxito", "Usuario eliminado correctamente.")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Ocurrió un error al eliminar el usuario: {str(e)}")
        else:
            QMessageBox.warning(self, "Advertencia", "Selecciona un usuario para eliminar")
            

