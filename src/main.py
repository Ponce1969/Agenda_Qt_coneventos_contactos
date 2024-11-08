import sys
import logging
import os
from pathlib import Path
from logging.handlers import RotatingFileHandler
from PyQt6.QtWidgets import QApplication, QDialog
from PyQt6.QtCore import Qt
from app import AgendaApp
from models.database import Database  # Importar la clase Database
from auth.login import LoginWindow  # Importar la clase LoginWindow
from auth.register import RegisterWindow  # Importar la clase RegisterWindow

def setup_logging():
    """
    Configura el sistema de logging de la aplicación.
    Solo registra errores y mantiene un máximo de 5 archivos de log.
    """
    # Definir la ruta específica para los logs
    log_path = Path("/home/gonzapython/Documentos/Agenda_qt/logs")
    
    # Asegurarse de que el directorio existe
    log_path.mkdir(parents=True, exist_ok=True)
    
    # Configurar el logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)  # Cambiar a INFO para registrar más detalles
    
    # Formato del log
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'  # Corregir 'levellevel' a 'levelname'
    )
    
    # Configurar RotatingFileHandler para mantener máximo 5 archivos
    log_file = log_path / 'agenda_error.log'
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=5*1024*1024,  # 5MB por archivo
        backupCount=4  # Mantener 4 backups (5 archivos en total)
    )
    file_handler.setLevel(logging.INFO)  # Cambiar a INFO para registrar más detalles
    file_handler.setFormatter(formatter)
    
    # Configurar StreamHandler para la consola (opcional)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)  # Cambiar a INFO para registrar más detalles
    console_handler.setFormatter(formatter)
    
    # Limpiar handlers existentes y agregar los nuevos
    logger.handlers = []
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

def setup_application():
    """Configura la aplicación Qt."""
    app = QApplication(sys.argv)
    
    # Configurar el estilo de la aplicación
    app.setStyle('Fusion')
    
    # Configurar atributos globales de la aplicación
    app.setApplicationName('Agenda de Reuniones')
    app.setApplicationVersion('1.0.0')
    app.setOrganizationName('GonzaPython')
    
    # Cargar y aplicar el archivo de estilos
    style_file = Path("/home/gonzapython/Documentos/Agenda_qt/styles/styles.qss")
    if style_file.exists():
        with open(style_file, "r") as file:
            app.setStyleSheet(file.read())
    
    return app

def check_environment():
    """Verifica y configura el entorno de la aplicación."""
    env_path = Path("/home/gonzapython/Documentos/Agenda_qt/.agen")
    if not env_path.exists():
        raise EnvironmentError("No se encuentra el entorno virtual de la aplicación")
    return True

def main():
    """Función principal de la aplicación."""
    logger = setup_logging()
    
    try:
        # Verificar entorno
        check_environment()
        
        # Crear y configurar la aplicación
        app = setup_application()
        
        # Inicializar la base de datos
        db_path = Path("/home/gonzapython/Documentos/Agenda_qt/base/agenda.db")
        db_path.parent.mkdir(parents=True, exist_ok=True)  # Asegurarse de que el directorio existe
        db = Database(db_path)
        
        # Verificar si hay usuarios en la base de datos
        if not db.hay_usuarios():
            # Mostrar la ventana de registro
            register_window = RegisterWindow(db)
            if register_window.exec() == QDialog.DialogCode.Accepted:
                # Obtener el usuario registrado
                user = db.verificar_usuario(register_window.username_input.text(), register_window.password_input.text())
                # Crear y mostrar la ventana principal
                ventana = AgendaApp(db, user)
                ventana.show()
                sys.exit(app.exec())
            else:
                sys.exit(0)
        else:
            # Mostrar la ventana de login
            login_window = LoginWindow(db)
            if login_window.exec() == QDialog.DialogCode.Accepted:
                # Obtener el usuario autenticado
                user = db.verificar_usuario(login_window.username_input.text(), login_window.password_input.text())
                # Crear y mostrar la ventana principal
                ventana = AgendaApp(db, user)
                ventana.show()
                sys.exit(app.exec())
            else:
                sys.exit(0)

    except Exception as e:
        logger.error(f"Error crítico en la aplicación: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()