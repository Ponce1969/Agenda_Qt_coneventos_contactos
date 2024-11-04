from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QMessageBox, QInputDialog, QCheckBox
)
from PyQt6.QtCore import Qt
from models.database import Database

class LoginWindow(QDialog):
    def __init__(self, db: Database):
        super().__init__()
        self.db = db
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Login")
        self.setGeometry(150, 150, 400, 200)
        
        # Layout principal
        self.layout = QVBoxLayout()
        
        # Campos de entrada
        self.username_label = QLabel("Username:")
        self.username_input = QLineEdit()
        
        self.password_label = QLabel("Password:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)  # Inicialmente oculta la contraseña
        
        # Checkbox para mostrar la contraseña
        self.show_password_checkbox = QCheckBox("Show Password")
        self.show_password_checkbox.stateChanged.connect(self.toggle_password_visibility)
        
        # Botones de acción
        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self.login)
        
        self.forgot_password_button = QPushButton("Forgot Password?")
        self.forgot_password_button.clicked.connect(self.forgot_password)
        
        # Añadir widgets al layout
        widgets = [
            self.username_label, self.username_input,
            self.password_label, self.password_input,
            self.show_password_checkbox, self.login_button, 
            self.forgot_password_button
        ]
        for widget in widgets:
            self.layout.addWidget(widget)
        
        self.setLayout(self.layout)

    def toggle_password_visibility(self, state):
        """Alterna la visibilidad de la contraseña según el estado del checkbox."""
        # Verifica si el checkbox está marcado
        if state == Qt.CheckState.Checked.value: # importante el .value para obtener el valor entero
            self.password_input.setEchoMode(QLineEdit.EchoMode.Normal)  # Muestra la contraseña
        else:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Password)  # Oculta la contraseña

    def login(self):
        """Verifica las credenciales del usuario y muestra un mensaje de éxito o error."""
        username = self.username_input.text()
        password = self.password_input.text()
        
        if not username or not password:
            QMessageBox.warning(self, "Error", "Username and password cannot be empty")
            return
        
        if self.db.verificar_usuario(username, password):
            self.accept()
        else:
            QMessageBox.warning(self, "Error", "Invalid username or password")

    def forgot_password(self):
        """Solicita un correo electrónico para la recuperación de contraseña."""
        email, ok = QInputDialog.getText(self, "Forgot Password", "Enter your email:")
        if ok and email:
            token = self.db.generar_token_recuperacion(email)
            if token:
                QMessageBox.information(self, "Success", f"Password reset token: {token}")
            else:
                QMessageBox.warning(self, "Error", "Email not found")

 