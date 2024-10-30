import sys
from datetime import datetime
from dataclasses import dataclass
from typing import List, Optional
from PyQt6.QtWidgets import (
    QMainWindow, QVBoxLayout, QWidget, QMessageBox,
    QCalendarWidget, QTableWidget, QTableWidgetItem, 
    QPushButton, QFileDialog, QHBoxLayout, QTimeEdit, QLabel, 
    QSplitter, QInputDialog, QHeaderView, QFormLayout, QToolBar
)
from PyQt6.QtCore import QDate, QTime, Qt, pyqtSlot
from PyQt6.QtGui import QIcon, QAction  # Importar QIcon y QAction desde PyQt6.QtGui
from database import Database
from alarma import Alarma  # Importar la clase Alarma
from ui_components import UIComponents  # Importar la clase UIComponents
from contactos import ContactosWindow  # Importar la clase ContactosWindow

@dataclass
class Evento:
    id: int  # Añadir un campo ID para identificar el evento en la base de datos
    fecha_hora: datetime
    descripcion: str

class AgendaApp(QMainWindow):
    def __init__(self, db: Database):
        super().__init__()
        self.db = db
        self.eventos: List[Evento] = []
        self.ui_components = UIComponents(self)  # Instanciar UIComponents
        self.initUI()  # Asegúrate de que este método esté definido
        self.setupConnections()
        self.cargar_eventos()
        self.alarma = Alarma(self)  # Inicializar la alarma

        # Cargar y aplicar el archivo QSS
        self.apply_stylesheet()

    def initUI(self):
        """Inicializa la interfaz de usuario"""
        self.setWindowTitle("Agenda de Reuniones y Eventos")
        self.setGeometry(100, 100, 800, 600)
        self.setWindowIcon(QIcon("/home/gonzapython/Documentos/Agenda_qt/iconos/book.png"))  # Configurar el icono de la ventana
        self.setupCentralWidget()
        self.setupLayouts()
        self.calendar, self.label_fecha = self.ui_components.setupCalendar(self.left_layout)
        self.tabla_eventos = self.ui_components.setupEventTable(self.left_layout)
        self.btn_agregar, self.btn_editar, self.btn_eliminar, self.btn_alarma = self.ui_components.setupButtons(self.right_layout)
        
        # Definir e inicializar time_edit
        self.time_edit = QTimeEdit()
        self.time_edit.setDisplayFormat("HH:mm")  # Configurar formato de 24 horas
        self.time_edit.setTime(QTime.currentTime())
        self.left_layout.addWidget(QLabel("Hora:"))
        self.left_layout.addWidget(self.time_edit)

        # Crear la barra de herramientas
        self.toolbar = QToolBar("Barra de Herramientas")
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.toolbar)
        
        # Añadir el botón de contactos a la barra de herramientas
        self.btn_contactos = QPushButton("Contactos")
        self.btn_contactos.clicked.connect(self.mostrar_contactos)
        self.toolbar.addWidget(self.btn_contactos)

        # Crear una barra de herramientas adicional para el botón de mostrar/ocultar
        self.toggle_toolbar = QToolBar("Toggle Toolbar")
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.toggle_toolbar)

        # Añadir un botón de icono para mostrar/ocultar la barra de herramientas
        self.toggle_toolbar_button = QPushButton()
        self.toggle_toolbar_button.setIcon(QIcon("/home/gonzapython/Documentos/Agenda_qt/iconos/tool_icon.png"))  # Asegúrate de que esta ruta sea correcta
        self.toggle_toolbar_button.setFixedSize(24, 24)
        self.toggle_toolbar_button.setStyleSheet("border: none;")
        self.toggle_toolbar_button.clicked.connect(self.toggle_toolbar_visibility)
        self.toggle_toolbar.addWidget(self.toggle_toolbar_button)

    def setupCentralWidget(self):
        """Configura el widget central"""
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)

    def setupLayouts(self):
        """Configura los layouts principales"""
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.main_layout.addWidget(self.splitter)

        # Widget izquierdo (80%)
        self.left_widget = QWidget()
        self.left_layout = QVBoxLayout(self.left_widget)
        self.splitter.addWidget(self.left_widget)
        self.splitter.setStretchFactor(0, 4)

        # Widget derecho (20%)
        self.right_widget = QWidget()
        self.right_layout = QVBoxLayout(self.right_widget)
        self.splitter.addWidget(self.right_widget)
        self.splitter.setStretchFactor(1, 1)

    def setupConnections(self):
        """Configura las conexiones de señales y slots"""
        self.calendar.clicked.connect(self.mostrar_fecha_seleccionada)
        self.btn_agregar.clicked.connect(self.agregar_evento)
        self.btn_editar.clicked.connect(self.editar_evento)
        self.btn_eliminar.clicked.connect(self.eliminar_evento)
        self.btn_alarma.clicked.connect(self.mostrar_alarma)  # Conectar el botón de alarma

    def cargar_eventos(self):
        """Carga los eventos desde la base de datos"""
        eventos_db = self.db.obtener_eventos()
        self.eventos.clear()  # Limpiar la lista de eventos antes de cargar
        for evento in eventos_db:
            fecha_hora = datetime.strptime(evento[1], '%Y-%m-%d %H:%M:%S')
            self.eventos.append(Evento(evento[0], fecha_hora, evento[2]))  # Incluir el ID del evento
        self.ui_components.actualizarTablaEventos(self.tabla_eventos, self.eventos)

    def validar_fecha_hora(self, fecha: str, hora: str) -> Optional[datetime]:
        """Valida el formato de fecha y hora"""
        try:
            fecha_hora_valida = datetime.strptime(f"{fecha} {hora}", '%Y-%m-%d %H:%M')
            if fecha_hora_valida < datetime.now():
                QMessageBox.warning(self, "Advertencia", "No puedes agregar eventos en el pasado.")
                return None
            return fecha_hora_valida
        except ValueError:
            QMessageBox.warning(self, "Advertencia", "Formato de fecha o hora no válido.")
            return None

    def actualizar_evento(self, evento: Evento):
        """Actualiza un evento en la base de datos y en la tabla"""
        try:
            self.db.editar_evento_completo(evento_id=evento.id, nueva_fecha_hora=evento.fecha_hora, nueva_descripcion=evento.descripcion)
            self.ui_components.actualizarTablaEventos(self.tabla_eventos, self.eventos)
            self.alarma.actualizar_lista_tareas()  # Actualizar la lista de tareas en la alarma
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Ocurrió un error al actualizar el evento: {str(e)}")

    def actualizar_tabla_inmediata(self, evento: Evento, accion: str):
        """Actualiza la tabla de eventos inmediatamente"""
        if accion == "agregar":
            row_position = self.tabla_eventos.rowCount()
            self.tabla_eventos.insertRow(row_position)
            self.tabla_eventos.setItem(row_position, 0, QTableWidgetItem(evento.fecha_hora.strftime('%Y-%m-%d')))
            self.tabla_eventos.setItem(row_position, 1, QTableWidgetItem(evento.fecha_hora.strftime('%H:%M')))
            self.tabla_eventos.setItem(row_position, 2, QTableWidgetItem(evento.descripcion))
        elif accion == "eliminar":
            self.tabla_eventos.removeRow(self.tabla_eventos.currentRow())

    @pyqtSlot()
    def mostrar_fecha_seleccionada(self):
        self.ui_components.seleccionarFecha(self.calendar, self.label_fecha)

    @pyqtSlot()
    def agregar_evento(self):
        fecha = self.calendar.selectedDate().toString('yyyy-MM-dd')
        hora = self.time_edit.time().toString('HH:mm')
        evento, ok = QInputDialog.getText(self, "Agregar Evento", "Descripción del evento:")
        if ok and evento:
            fecha_hora_valida = self.validar_fecha_hora(fecha, hora)
            if fecha_hora_valida is None:
                return
            try:
                self.db.agregar_evento(fecha, hora, evento)
                nuevo_evento_id = self.db.obtener_eventos()[-1][0]
                nuevo_evento = Evento(nuevo_evento_id, fecha_hora_valida, evento)
                self.eventos.append(nuevo_evento)
                self.actualizar_tabla_inmediata(nuevo_evento, "agregar")
                self.alarma.actualizar_lista_tareas()  # Actualizar la lista de tareas en la alarma
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Ocurrió un error al agregar el evento: {str(e)}")

    @pyqtSlot()
    def editar_evento(self):
        selected_row = self.tabla_eventos.currentRow()
        if selected_row >= 0:
            evento = self.eventos[selected_row]
            
            # Crear diálogos para editar la fecha, hora y descripción
            nueva_fecha, ok_fecha = QInputDialog.getText(self, "Editar Fecha", "Fecha del evento (yyyy-MM-dd):", text=evento.fecha_hora.strftime('%Y-%m-%d'))
            nueva_hora, ok_hora = QInputDialog.getText(self, "Editar Hora", "Hora del evento (HH:mm):", text=evento.fecha_hora.strftime('%H:%M'))
            nueva_descripcion, ok_desc = QInputDialog.getText(self, "Editar Evento", "Descripción del evento:", text=evento.descripcion)
            
            if ok_fecha and ok_hora and ok_desc:
                fecha_hora_valida = self.validar_fecha_hora(nueva_fecha, nueva_hora)
                if fecha_hora_valida is None:
                    return
                evento.fecha_hora = fecha_hora_valida
                evento.descripcion = nueva_descripcion
                self.actualizar_evento(evento)
        else:
            QMessageBox.warning(self, "Advertencia", "Selecciona un evento para editar")

    @pyqtSlot()
    def eliminar_evento(self):
        selected_row = self.tabla_eventos.currentRow()
        if selected_row >= 0:
            # Confirmación antes de eliminar
            respuesta = QMessageBox.question(self, "Confirmación", "¿Estás seguro de que deseas eliminar este evento?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if respuesta == QMessageBox.StandardButton.Yes:
                evento = self.eventos[selected_row]
                try:
                    self.db.eliminar_evento(evento_id=evento.id)  # Eliminar de la base de datos
                    del self.eventos[selected_row]  # Eliminar de la lista de eventos
                    self.actualizar_tabla_inmediata(evento, "eliminar")
                    self.alarma.actualizar_lista_tareas()  # Actualizar la lista de tareas en la alarma
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Ocurrió un error al eliminar el evento: {str(e)}")
        else:
            QMessageBox.warning(self, "Advertencia", "Selecciona un evento para eliminar")

    @pyqtSlot()
    def mostrar_alarma(self):
        self.alarma.show()

    @pyqtSlot()
    def mostrar_contactos(self):
        self.contactos_window = ContactosWindow(self.db)
        self.contactos_window.exec()  # Cambiar de show() a exec() para hacer la ventana modal

    def actualizar_tabla(self):
        """Actualiza la tabla de eventos"""
        self.ui_components.actualizarTablaEventos(self.tabla_eventos, self.eventos)

    def apply_stylesheet(self):
        """Carga y aplica el archivo QSS"""
        with open("/home/gonzapython/Documentos/Agenda_qt/styles/styles.qss", "r") as file:
            self.setStyleSheet(file.read())

    @pyqtSlot()
    def toggle_toolbar_visibility(self):
        """Muestra u oculta la barra de herramientas"""
        if self.toolbar.isVisible():
            self.toolbar.hide()
        else:
            self.toolbar.show()

