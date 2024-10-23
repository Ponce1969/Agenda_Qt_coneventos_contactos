import sys
from PyQt6.QtWidgets import (
    QMainWindow, QVBoxLayout, QWidget, QMessageBox,
    QCalendarWidget, QTableWidget, QTableWidgetItem, 
    QPushButton, QFileDialog, QHBoxLayout, QTimeEdit, QLabel, 
    QLineEdit, QSplitter, QInputDialog, QHeaderView
)
from PyQt6.QtCore import QDate, QTime, Qt


class AgendaApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # Configuración de la ventana principal
        self.setWindowTitle("Agenda de Reuniones y Eventos")
        self.setGeometry(100, 100, 800, 600)

        # Widget central
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        # Layout principal horizontal
        main_layout = QHBoxLayout(central_widget)

        # Splitter para dividir el espacio
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)

        # Layout izquierdo (80%)
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        splitter.addWidget(left_widget)
        splitter.setStretchFactor(0, 4)

        # Layout derecho (20%)
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        splitter.addWidget(right_widget)
        splitter.setStretchFactor(1, 1)

        # Widget calendario
        self.calendar = QCalendarWidget(self)
        self.calendar.setGridVisible(True)
        self.calendar.clicked.connect(self.mostrar_fecha_seleccionada)

        # Hora y Fecha
        self.label_fecha = QLabel("Fecha seleccionada: ")
        self.time_edit = QTimeEdit(self)
        self.time_edit.setTime(QTime.currentTime())

       

        # Tabla para mostrar eventos
        self.tabla_eventos = QTableWidget(self)
        self.tabla_eventos.setColumnCount(3)
        self.tabla_eventos.setHorizontalHeaderLabels(["Fecha", "Hora", "Evento"])
        
        # Ajustar el tamaño de las columnas
        header = self.tabla_eventos.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents) 
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        
        
        # Añadir widgets al layout izquierdo
        left_layout.addWidget(self.calendar)
        left_layout.addWidget(self.label_fecha)
        left_layout.addWidget(QLabel("Hora:"))
        left_layout.addWidget(self.time_edit)
        left_layout.addWidget(self.tabla_eventos)

        # Botones para añadir, editar, eliminar eventos
        self.btn_agregar = QPushButton("Agregar Evento", self)
        self.btn_editar = QPushButton("Editar Evento", self)
        self.btn_eliminar = QPushButton("Eliminar Evento", self)

        # Añadir botones al layout derecho
        right_layout.addWidget(self.btn_agregar)
        right_layout.addWidget(self.btn_editar)
        right_layout.addWidget(self.btn_eliminar)
        right_layout.addStretch()

        # Conectar botones a métodos
        self.btn_agregar.clicked.connect(self.agregar_evento)
        self.btn_editar.clicked.connect(self.editar_evento)
        self.btn_eliminar.clicked.connect(self.eliminar_evento)

    def mostrar_fecha_seleccionada(self):
        fecha = self.calendar.selectedDate()
        self.label_fecha.setText(f"Fecha seleccionada: {fecha.toString('yyyy-MM-dd')}")

    def agregar_evento(self):
        # Obtener la fecha y hora seleccionadas
        fecha = self.calendar.selectedDate().toString('yyyy-MM-dd')
        hora = self.time_edit.time().toString('HH:mm')

        # Abrir un cuadro de diálogo para ingresar la descripción del evento
        evento, ok = QInputDialog.getText(self, "Agregar Evento", "Descripción del evento:")
        if ok and evento:
            # Agregar el evento a la tabla
            row_position = self.tabla_eventos.rowCount()
            self.tabla_eventos.insertRow(row_position)
            self.tabla_eventos.setItem(row_position, 0, QTableWidgetItem(fecha))
            self.tabla_eventos.setItem(row_position, 1, QTableWidgetItem(hora))
            self.tabla_eventos.setItem(row_position, 2, QTableWidgetItem(evento))

    def editar_evento(self):
        # Editar evento seleccionado en la tabla
        selected_row = self.tabla_eventos.currentRow()
        if selected_row >= 0:
            fecha = self.tabla_eventos.item(selected_row, 0).text()
            hora = self.tabla_eventos.item(selected_row, 1).text()
            evento = self.tabla_eventos.item(selected_row, 2).text()

            # Abrir un cuadro de diálogo para editar la descripción del evento
            evento, ok = QInputDialog.getText(self, "Editar Evento", "Descripción del evento:", text=evento)
            if ok and evento:
                self.tabla_eventos.setItem(selected_row, 2, QTableWidgetItem(evento))
        else:
            # Mostrar una alerta si no hay un evento seleccionado
            QMessageBox.warning(self, "Advertencia", "Selecciona un evento para editar")
            

    def eliminar_evento(self):
        # Eliminar evento seleccionado en la tabla
        selected_row = self.tabla_eventos.currentRow()
        if selected_row >= 0:
            self.tabla_eventos.removeRow(selected_row)

   


