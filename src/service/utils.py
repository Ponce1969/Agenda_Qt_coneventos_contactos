# utils.py

from datetime import datetime
from typing import Optional
from PyQt6.QtWidgets import QMessageBox, QTableWidgetItem
from models.models import Evento

def validar_fecha_hora(parent, fecha: str, hora: str) -> Optional[datetime]:
    try:
        fecha_hora_valida = datetime.strptime(f"{fecha} {hora}", '%Y-%m-%d %H:%M')
        if fecha_hora_valida < datetime.now():
            QMessageBox.warning(parent, "Advertencia", "No puedes agregar eventos en el pasado.")
            return None
        return fecha_hora_valida
    except ValueError:
        QMessageBox.warning(parent, "Advertencia", "Formato de fecha o hora no válido.")
        return None

def actualizar_tabla_inmediata(tabla_eventos, evento: Evento, accion: str):
    if accion == "agregar":
        row_position = tabla_eventos.rowCount()
        tabla_eventos.insertRow(row_position)
        tabla_eventos.setItem(row_position, 0, QTableWidgetItem(evento.fecha_hora.strftime('%Y-%m-%d')))
        tabla_eventos.setItem(row_position, 1, QTableWidgetItem(evento.fecha_hora.strftime('%H:%M')))
        tabla_eventos.setItem(row_position, 2, QTableWidgetItem(evento.descripcion))
    elif accion == "eliminar":
        tabla_eventos.removeRow(tabla_eventos.currentRow()) 