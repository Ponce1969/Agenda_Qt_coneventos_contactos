import sys
import logging
import os
from pathlib import Path
from logging.handlers import RotatingFileHandler
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from app import AgendaApp
from database import Database  # Importar la clase Database

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
    logger.setLevel(logging.ERROR)  # Solo registrar errores
    
    # Formato del log
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Configurar RotatingFileHandler para mantener máximo 5 archivos
    log_file = log_path / 'agenda_error.log'
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=5*1024*1024,  # 5MB por archivo
        backupCount=4  # Mantener 4 backups (5 archivos en total)
    )
    file_handler.setLevel(logging.ERROR)
    file_handler.setFormatter(formatter)
    
    # Configurar StreamHandler para la consola (opcional)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.ERROR)
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
        
        # Crear y mostrar la ventana principal
        ventana = AgendaApp(db)  # Pasar la instancia de Database a AgendaApp
        ventana.show()

        # Ejecutar el loop principal de la aplicación
        sys.exit(app.exec())

    except Exception as e:
        logger.error(f"Error crítico en la aplicación: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()