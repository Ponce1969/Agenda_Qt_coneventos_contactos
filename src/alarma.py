import logging
from PyQt6.QtCore import QTimer, QDateTime, Qt
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QListWidget, QPushButton, QMessageBox
from playsound import playsound
from datetime import datetime, timedelta

class Alarma(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.sonido_alarma = "/home/gonzapython/Documentos/Agenda_qt/sonido/alarma.wav"
        
        self.setWindowTitle("Configuración de Alarma")
        self.setGeometry(100, 100, 400, 300)
        
        self.layout = QVBoxLayout()
        self.label_tareas = QLabel("Tareas del día:")
        self.layout.addWidget(self.label_tareas)
        
        self.lista_tareas = QListWidget()
        self.layout.addWidget(self.lista_tareas)
        
        # Botón para cerrar la ventana de configuración
        self.btn_cerrar = QPushButton("Cerrar")
        self.btn_cerrar.clicked.connect(self.close)
        self.layout.addWidget(self.btn_cerrar)
        
        self.setLayout(self.layout)
        
        # Llamar a cargar_tareas para llenar la lista al iniciar
        self.cargar_tareas()
        
        # Crear un temporizador para verificar las alarmas cada minuto
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.verificar_alarma)
        self.timer.start(60000)  # Verifica cada 60 segundos (1 minuto)
    
    def verificar_alarma(self):
        """Verifica si hay algún evento próximo y muestra las notificaciones o reproduce la alarma."""
        ahora = QDateTime.currentDateTime().toPyDateTime()  # Obtener la hora actual como objeto datetime
        
        for evento in self.parent.eventos:
            evento_fecha_hora = evento.fecha_hora  # Usar el atributo fecha_hora directamente
            diferencia = evento_fecha_hora - ahora

            # Comprobar si queda 1 hora para el evento
            if timedelta(minutes=59) < diferencia <= timedelta(hours=1):
                self.mostrar_aviso(f"Queda 1 hora para tu evento: {evento.descripcion}")
            
            # Comprobar si queda 15 minutos para el evento
            elif timedelta(minutes=14) < diferencia <= timedelta(minutes=15):
                self.mostrar_aviso(f"Quedan 15 minutos para tu evento: {evento.descripcion}")
            
            # Comprobar si es la hora del evento y reproducir la alarma
            elif timedelta(seconds=0) <= diferencia <= timedelta(minutes=1):
                self.reproducir_alarma(evento.descripcion)
    
    def mostrar_aviso(self, mensaje):
        """Muestra una advertencia con un mensaje."""
        logging.info(f"Mostrando aviso: {mensaje}")
        QMessageBox.warning(self, "Recordatorio de Evento", mensaje, QMessageBox.StandardButton.Ok)

    def reproducir_alarma(self, descripcion_evento):
        """Reproduce el sonido de la alarma y muestra un aviso."""
        logging.info(f"Reproduciendo alarma para el evento: {descripcion_evento}")
        try:
            playsound(self.sonido_alarma)  # Reproducir sonido de la alarma
        except Exception as e:
            logging.error(f"Error al reproducir el sonido de la alarma: {e}")
            QMessageBox.warning(self, "Error", "No se pudo reproducir el sonido de la alarma.")
        
        QMessageBox.information(self, "Alarma de Evento", f"Es la hora del evento: {descripcion_evento}", QMessageBox.StandardButton.Ok)

    def cargar_tareas(self):
        """Carga las tareas del día en la lista."""
        self.lista_tareas.clear()  # Limpiar la lista
        hoy = QDateTime.currentDateTime().toString('yyyy-MM-dd')
        
        for evento in self.parent.eventos:
            if evento.fecha_hora.strftime('%Y-%m-%d') == hoy:
                self.lista_tareas.addItem(f"{evento.fecha_hora.strftime('%H:%M')} - {evento.descripcion}")

    def actualizar_lista_tareas(self):
        """Actualiza la lista de tareas manualmente."""
        self.cargar_tareas()

    def closeEvent(self, event):
        """Sobrescribe el evento de cierre para actualizar la lista de tareas al reabrir."""
        self.cargar_tareas()
        super().closeEvent(event)

