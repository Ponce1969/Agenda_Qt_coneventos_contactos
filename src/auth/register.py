from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
)
from models.database import Database

class RegisterWindow(QDialog):
    def __init__(self, db: Database):
        super().__init__()
        self.db = db
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Register")
        self.setGeometry(150, 150, 400, 300)
        
        self.layout = QVBoxLayout()
        
        self.username_label = QLabel("Username:")
        self.username_input = QLineEdit()
        
        self.password_label = QLabel("Password:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        
        self.email_label = QLabel("Email:")
        self.email_input = QLineEdit()
        
        self.register_button = QPushButton("Register")
        self.register_button.clicked.connect(self.register)
        
        for widget in [self.username_label, self.username_input,
                      self.password_label, self.password_input,
                      self.email_label, self.email_input,
                      self.register_button]:
            self.layout.addWidget(widget)
        
        self.setLayout(self.layout)

    def register(self):
        username = self.username_input.text()
        password = self.password_input.text()
        email = self.email_input.text()
        
        if username and password and email:
            try:
                self.db.agregar_usuario(username, password, email, "admin")
                QMessageBox.information(self, "Success", "User registered successfully")
                self.accept()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error registering user: {str(e)}")
        else:
            QMessageBox.warning(self, "Error", "All fields are required")