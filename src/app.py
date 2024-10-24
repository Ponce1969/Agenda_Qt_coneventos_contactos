import sys
from datetime import datetime
from dataclasses import dataclass
from typing import List, Optional
from PyQt6.QtWidgets import (
    QMainWindow, QVBoxLayout, QWidget, QMessageBox,
    QCalendarWidget, QTableWidget, QTableWidgetItem, 
    QPushButton, QFileDialog, QHBoxLayout, QTimeEdit, QLabel, 
    QSplitter, QInputDialog, QHeaderView
)
from PyQt6.QtCore import QDate, QTime, Qt, pyqtSlot
from database import Database

@dataclass
class Evento:
    fecha: str
    hora: str
    descripcion: str

class AgendaApp(QMainWindow):
    def __init__(self, db: Database):
        super().__init__()
        self.db = db
        self.eventos: List[Evento] = []
        self.initUI()
        self.setupConnections()
        self.cargar_eventos()

    def initUI(self):
        """Inicializa la interfaz de usuario"""
        self.setWindowTitle("Agenda de Reuniones y Eventos")
        self.setGeometry(100, 100, 800, 600)
        self.setupCentralWidget()
        self.setupLayouts()
        self.setupCalendar()
        self.setupTimeWidget()
        self.setupEventTable()
        self.setupButtons()

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

    def setupCalendar(self):
        """Configura el widget de calendario"""
        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        self.label_fecha = QLabel("Fecha seleccionada: ")
        self.left_layout.addWidget(self.calendar)
        self.left_layout.addWidget(self.label_fecha)

    def setupTimeWidget(self):
        """Configura el widget de tiempo"""
        self.time_edit = QTimeEdit()
        self.time_edit.setTime(QTime.currentTime())
        self.left_layout.addWidget(QLabel("Hora:"))
        self.left_layout.addWidget(self.time_edit)

    def setupEventTable(self):
        """Configura la tabla de eventos"""
        self.tabla_eventos = QTableWidget()
        self.tabla_eventos.setColumnCount(3)
        self.tabla_eventos.setHorizontalHeaderLabels(["Fecha", "Hora", "Evento"])
        
        header = self.tabla_eventos.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)

        self.left_layout.addWidget(self.tabla_eventos)

    def setupButtons(self):
        """Configura los botones"""
        self.btn_agregar = QPushButton("Agregar Evento")
        self.btn_editar = QPushButton("Editar Evento")
        self.btn_eliminar = QPushButton("Eliminar Evento")

        self.right_layout.addWidget(self.btn_agregar)
        self.right_layout.addWidget(self.btn_editar)
        self.right_layout.addWidget(self.btn_eliminar)
        self.right_layout.addStretch()

    def setupConnections(self):
        """Configura las conexiones de señales y slots"""
        self.calendar.clicked.connect(self.mostrar_fecha_seleccionada)
        self.btn_agregar.clicked.connect(self.agregar_evento)
        self.btn_editar.clicked.connect(self.editar_evento)
        self.btn_eliminar.clicked.connect(self.eliminar_evento)

    def cargar_eventos(self):
        """Carga los eventos desde la base de datos"""
        eventos_db = self.db.obtener_eventos()
        for evento in eventos_db:
            self.eventos.append(Evento(evento[1], evento[2], evento[3]))
        self.actualizar_tabla()

    @pyqtSlot()
    def mostrar_fecha_seleccionada(self):
        fecha = self.calendar.selectedDate()
        self.label_fecha.setText(f"Fecha seleccionada: {fecha.toString('yyyy-MM-dd')}")

    @pyqtSlot()
    def agregar_evento(self):
        fecha = self.calendar.selectedDate().toString('yyyy-MM-dd')
        hora = self.time_edit.time().toString('HH:mm')
        evento, ok = QInputDialog.getText(self, "Agregar Evento", "Descripción del evento:")
        if ok and evento:
            nuevo_evento = Evento(fecha, hora, evento)
            self.eventos.append(nuevo_evento)
            self.db.agregar_evento(fecha, hora, evento)
            self.actualizar_tabla()

    @pyqtSlot()
    def editar_evento(self):
        selected_row = self.tabla_eventos.currentRow()
        if selected_row >= 0:
            evento = self.eventos[selected_row]
            nueva_descripcion, ok = QInputDialog.getText(self, "Editar Evento", "Descripción del evento:", text=evento.descripcion)
            if ok and nueva_descripcion:
                evento.descripcion = nueva_descripcion
                self.db.editar_evento(evento_id=selected_row + 1, nueva_descripcion=nueva_descripcion)  # Asumiendo que el ID es el índice + 1
                self.actualizar_tabla()
        else:
            QMessageBox.warning(self, "Advertencia", "Selecciona un evento para editar")

    @pyqtSlot()
    def eliminar_evento(self):
        selected_row = self.tabla_eventos.currentRow()
        if selected_row >= 0:
            del self.eventos[selected_row]
            self.db.eliminar_evento(evento_id=selected_row + 1)  # Asumiendo que el ID es el índice + 1
            self.actualizar_tabla()
        else:
            QMessageBox.warning(self, "Advertencia", "Selecciona un evento para eliminar")

    def actualizar_tabla(self):
        """Actualiza la tabla de eventos"""
        self.tabla_eventos.setRowCount(0)
        for evento in self.eventos:
            row_position = self.tabla_eventos.rowCount()
            self.tabla_eventos.insertRow(row_position)
            self.tabla_eventos.setItem(row_position, 0, QTableWidgetItem(evento.fecha))
            self.tabla_eventos.setItem(row_position, 1, QTableWidgetItem(evento.hora))
            self.tabla_eventos.setItem(row_position, 2, QTableWidgetItem(evento.descripcion))
   


