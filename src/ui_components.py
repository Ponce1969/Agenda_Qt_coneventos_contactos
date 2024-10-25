from PyQt6.QtWidgets import (
    QVBoxLayout, QLabel, QCalendarWidget, QTableWidget, QPushButton, QFormLayout, QHeaderView, QTableWidgetItem
)
from PyQt6.QtCore import Qt
from typing import List, Tuple

class UIComponents:
    def __init__(self, parent):
        """
        Inicializa el objeto de componentes de la UI.
        :param parent: La ventana principal que utiliza estos componentes.
        """
        self.parent = parent

    def setupCalendar(self, layout: QVBoxLayout) -> Tuple[QCalendarWidget, QLabel]:
        """
        Configura el widget de calendario.
        :param layout: El layout donde se agregará el calendario y la etiqueta de fecha seleccionada.
        :return: El widget de calendario y el label de la fecha seleccionada.
        """
        calendar = QCalendarWidget()
        calendar.setGridVisible(True)
        
        label_fecha = QLabel("Fecha seleccionada: ")
        
        layout.addWidget(calendar)
        layout.addWidget(label_fecha)
        
        return calendar, label_fecha

    def setupEventTable(self, layout: QVBoxLayout) -> QTableWidget:
        """
        Configura la tabla de eventos.
        :param layout: El layout donde se agregará la tabla de eventos.
        :return: El widget de tabla de eventos.
        """
        tabla_eventos = QTableWidget()
        tabla_eventos.setColumnCount(3)
        tabla_eventos.setHorizontalHeaderLabels(["Fecha", "Hora", "Evento"])

        header = tabla_eventos.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)

        layout.addWidget(tabla_eventos)
        return tabla_eventos

    def setupButtons(self, layout: QVBoxLayout) -> Tuple[QPushButton, QPushButton, QPushButton, QPushButton]:
        """
        Configura los botones de la aplicación.
        :param layout: El layout donde se agregarán los botones.
        :return: Los botones de agregar, editar, eliminar y alarma.
        """
        btn_agregar = QPushButton("Agregar Evento")
        btn_editar = QPushButton("Editar Evento")
        btn_eliminar = QPushButton("Eliminar Evento")
        btn_alarma = QPushButton("Configurar Alarma")

        layout.addWidget(btn_agregar)
        layout.addWidget(btn_editar)
        layout.addWidget(btn_eliminar)
        layout.addWidget(btn_alarma)
        layout.addStretch()

        return btn_agregar, btn_editar, btn_eliminar, btn_alarma

    def actualizarTablaEventos(self, tabla_eventos: QTableWidget, eventos: List) -> None:
        """
        Actualiza la tabla de eventos con los datos proporcionados.
        :param tabla_eventos: El widget de tabla de eventos.
        :param eventos: Lista de eventos que deben mostrarse en la tabla.
        """
        tabla_eventos.setRowCount(0)  # Limpiar la tabla antes de actualizar
        for evento in eventos:
            row_position = tabla_eventos.rowCount()
            tabla_eventos.insertRow(row_position)
            tabla_eventos.setItem(row_position, 0, QTableWidgetItem(evento.fecha_hora.strftime('%Y-%m-%d')))
            tabla_eventos.setItem(row_position, 1, QTableWidgetItem(evento.fecha_hora.strftime('%H:%M')))
            tabla_eventos.setItem(row_position, 2, QTableWidgetItem(evento.descripcion))

    def seleccionarFecha(self, calendar: QCalendarWidget, label_fecha: QLabel) -> None:
        """
        Actualiza la etiqueta con la fecha seleccionada en el calendario.
        :param calendar: El widget de calendario.
        :param label_fecha: El label donde se mostrará la fecha seleccionada.
        """
        fecha = calendar.selectedDate()
        label_fecha.setText(f"Fecha seleccionada: {fecha.toString('yyyy-MM-dd')}")

    def limpiarCampos(self, tabla_eventos: QTableWidget, label_fecha: QLabel) -> None:
        """
        Limpia la tabla de eventos y la etiqueta de fecha seleccionada.
        :param tabla_eventos: La tabla de eventos.
        :param label_fecha: El label de fecha seleccionada.
        """
        tabla_eventos.setRowCount(0)
        label_fecha.setText("Fecha seleccionada: ")

