from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, 
    QTableWidget, QTableWidgetItem, QMessageBox, QInputDialog
)
from models.database import Database

class GestionarUsuariosWindow(QDialog):
    def __init__(self, db: Database):
        super().__init__()
        self.db = db
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Gestionar Usuarios")
        self.setGeometry(150, 150, 600, 400)
        
        self.layout = QVBoxLayout()
        
        # Tabla de usuarios
        self.tabla_usuarios = QTableWidget()
        self.tabla_usuarios.setColumnCount(4)
        self.tabla_usuarios.setHorizontalHeaderLabels(["ID", "Username", "Email", "Role"])
        self.tabla_usuarios.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla_usuarios.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.layout.addWidget(self.tabla_usuarios)

        # Botones para agregar y eliminar usuarios
        self.btn_agregar = QPushButton("Agregar Usuario")
        self.btn_agregar.clicked.connect(self.agregar_usuario)
        self.layout.addWidget(self.btn_agregar)

        self.setLayout(self.layout)
        self.cargar_usuarios()

    def cargar_usuarios(self):
        """Carga los usuarios desde la base de datos"""
        usuarios = self.db.obtener_usuarios()
        self.tabla_usuarios.setRowCount(0)
        for usuario in usuarios:
            row_position = self.tabla_usuarios.rowCount()
            self.tabla_usuarios.insertRow(row_position)
            self.tabla_usuarios.setItem(row_position, 0, QTableWidgetItem(str(usuario[0])))
            self.tabla_usuarios.setItem(row_position, 1, QTableWidgetItem(usuario[1]))
            self.tabla_usuarios.setItem(row_position, 2, QTableWidgetItem(usuario[2]))
            self.tabla_usuarios.setItem(row_position, 3, QTableWidgetItem(usuario[3]))

    def agregar_usuario(self):
        """Agrega un nuevo usuario"""
        username, ok_username = QInputDialog.getText(self, "Agregar Usuario", "Nombre de usuario:")
        if not ok_username or not username:
            return

        password, ok_password = QInputDialog.getText(self, "Agregar Usuario", "Contraseña:", QLineEdit.EchoMode.Password)
        if not ok_password or not password:
            return

        email, ok_email = QInputDialog.getText(self, "Agregar Usuario", "Correo electrónico:")
        if not ok_email or not email:
            return

        try:
            self.db.agregar_usuario(username, password, email, "user")
            QMessageBox.information(self, "Éxito", "Usuario agregado correctamente")
            self.cargar_usuarios()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Ocurrió un error al agregar el usuario: {str(e)}")