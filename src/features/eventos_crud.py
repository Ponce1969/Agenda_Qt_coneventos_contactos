# features/eventos_crud.py
from models.models import Evento
from PyQt6.QtWidgets import QMessageBox
from datetime import datetime

def agregar_evento_crud(db, fecha, hora, descripcion):
    try:
        db.agregar_evento(fecha, hora, descripcion)
        nuevo_evento_id = db.obtener_eventos()[-1][0]
        fecha_hora_valida = datetime.strptime(f"{fecha} {hora}", '%Y-%m-%d %H:%M')
        nuevo_evento = Evento(nuevo_evento_id, fecha_hora_valida, descripcion)
        return nuevo_evento
    except Exception as e:
        QMessageBox.critical(None, "Error", f"Ocurrió un error al agregar el evento: {str(e)}")
        return None

def editar_evento_crud(db, evento, nueva_fecha, nueva_hora, nueva_descripcion):
    try:
        fecha_hora_valida = datetime.strptime(f"{nueva_fecha} {nueva_hora}", '%Y-%m-%d %H:%M')
        db.editar_evento_completo(
            evento_id=evento.id,
            nueva_fecha_hora=fecha_hora_valida,
            nueva_descripcion=nueva_descripcion
        )
        evento.fecha_hora = fecha_hora_valida
        evento.descripcion = nueva_descripcion
        return evento
    except Exception as e:
        QMessageBox.critical(None, "Error", f"Ocurrió un error al actualizar el evento: {str(e)}")
        return None

def eliminar_evento_crud(db, evento):
    try:
        db.eliminar_evento(evento_id=evento.id)
        return True
    except Exception as e:
        QMessageBox.critical(None, "Error", f"Ocurrió un error al eliminar el evento: {str(e)}")
        return False