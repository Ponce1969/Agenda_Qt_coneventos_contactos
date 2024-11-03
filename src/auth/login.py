from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QInputDialog
)
from models.database import Database

class LoginWindow(QDialog):
    def __init__(self, db: Database):
        super().__init__()
        self.db = db
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Login")
        self.setGeometry(150, 150, 400, 200)
        
        self.layout = QVBoxLayout()
        
        self.username_label = QLabel("Username:")
        self.username_input = QLineEdit()
        
        self.password_label = QLabel("Password:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        
        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self.login)
        
        self.forgot_password_button = QPushButton("Forgot Password?")
        self.forgot_password_button.clicked.connect(self.forgot_password)
        
        for widget in [self.username_label, self.username_input,
                      self.password_label, self.password_input,
                      self.login_button, self.forgot_password_button]:
            self.layout.addWidget(widget)
        
        self.setLayout(self.layout)

    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        
        user = self.db.verificar_usuario(username, password)
        if user:
            self.accept()
        else:
            QMessageBox.warning(self, "Error", "Invalid username or password")

    def forgot_password(self):
        email, ok = QInputDialog.getText(self, "Forgot Password", "Enter your email:")
        if ok and email:
            token = self.db.generar_token_recuperacion(email)
            if token:
                # Aquí deberías enviar el token al correo electrónico del usuario
                QMessageBox.information(self, "Success", f"Password reset token: {token}")
            else:
                QMessageBox.warning(self, "Error", "Email not found")