from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
)
from models.database import Database

class ResetPasswordWindow(QDialog):
    def __init__(self, db: Database, token: str):
        super().__init__()
        self.db = db
        self.token = token
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Reset Password")
        self.setGeometry(150, 150, 400, 200)
        
        self.layout = QVBoxLayout()
        
        self.new_password_label = QLabel("New Password:")
        self.new_password_input = QLineEdit()
        self.new_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        
        self.confirm_password_label = QLabel("Confirm Password:")
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        
        self.reset_button = QPushButton("Reset Password")
        self.reset_button.clicked.connect(self.reset_password)
        
        for widget in [self.new_password_label, self.new_password_input,
                      self.confirm_password_label, self.confirm_password_input,
                      self.reset_button]:
            self.layout.addWidget(widget)
        
        self.setLayout(self.layout)

    def reset_password(self):
        new_password = self.new_password_input.text()
        confirm_password = self.confirm_password_input.text()
        
        if new_password != confirm_password:
            QMessageBox.warning(self, "Error", "Passwords do not match")
            return
        
        reset = self.db.verificar_token_recuperacion(self.token)
        if reset:
            self.db.cambiar_contrasena(reset[1], new_password)
            QMessageBox.information(self, "Success", "Password has been reset")
            self.accept()
        else:
            QMessageBox.warning(self, "Error", "Invalid or expired token")