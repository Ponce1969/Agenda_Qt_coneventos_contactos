import sys
from datetime import datetime
import time
from typing import List, Optional
from PyQt6.QtWidgets import (
    QMainWindow, QVBoxLayout, QWidget, QMessageBox,
    QCalendarWidget, QTableWidget, QTableWidgetItem, 
    QPushButton, QHBoxLayout, QTimeEdit, QLabel, 
    QSplitter, QInputDialog, QToolBar, QLineEdit, QFileDialog
)
from PyQt6.QtCore import QDate, QTime, Qt, pyqtSlot
from PyQt6.QtGui import QIcon
from models.database import Database
from features.alarma import Alarma
from ui.ui_components import UIComponents
from features.contactos import ContactosWindow
from models.models import Evento
from features.compras import ComprasWindow
from auth.gestionar_usuarios import GestionarUsuariosWindow  # Importar la clase GestionarUsuariosWindow
from  features.export_agenda import exportar_csv, exportar_json, exportar_xml, importar_csv, importar_json, importar_xml
import csv
import json
import xml.etree.ElementTree as ET

class AgendaApp(QMainWindow):
    def __init__(self, db: Database, user):  # Pasar el usuario actual
        super().__init__()  # Inicializar la clase base
        self.db = db   # Guardar la instancia de la base de datos
        self.user = user  # Guardar el usuario actual
        self.eventos: List[Evento] = []        # Lista para almacenar los eventos
        self.ui_components = UIComponents(self) # Crear una instancia de UIComponents
        self.initUI() # Inicializar la interfaz de usuario
        self.setupConnections()# Configurar las conexiones de señales y slots
        self.cargar_eventos()# Cargar los eventos desde la base de datos
        self.alarma = Alarma(self)  # Crear instancia de Alarma
        self.bloqueado_hasta = None  # Inicializar el tiempo de bloqueo

        # Cargar y aplicar el archivo QSS
        self.apply_stylesheet()

    def initUI(self):
        """Inicializa la interfaz de usuario"""
        self.setWindowTitle("Agenda de Reuniones y Eventos")
        self.setGeometry(100, 100, 800, 600)
        self.setWindowIcon(QIcon("/home/gonzapython/Documentos/Agenda_qt/iconos/book.png"))
        self.setupCentralWidget()
        self.setupLayouts()
        self.calendar, self.label_fecha = self.ui_components.setupCalendar(self.left_layout)
        self.tabla_eventos = self.ui_components.setupEventTable(self.left_layout)
        self.btn_agregar, self.btn_editar, self.btn_eliminar, self.btn_alarma = self.ui_components.setupButtons(self.right_layout)
        
        # Deshabilitar el botón de eliminar si el usuario no es administrador
        if self.user[4] != 'admin':
            self.btn_eliminar.setDisabled(True)
        
        # Definir e inicializar time_edit
        self.time_edit = QTimeEdit()
        self.time_edit.setDisplayFormat("HH:mm")
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

        # Añadir el botón de compras a la barra de herramientas
        self.btn_compras = QPushButton("Compras")
        self.btn_compras.clicked.connect(self.mostrar_compras)
        self.toolbar.addWidget(self.btn_compras)

        # Añadir el botón de gestionar usuarios a la barra de herramientas
        self.btn_gestionar_usuarios = QPushButton("Gestionar Usuarios")
        self.btn_gestionar_usuarios.clicked.connect(self.gestionar_usuarios)
        self.toolbar.addWidget(self.btn_gestionar_usuarios)
        
        # Añadir el botón de exportar a la barra de herramientas
        self.btn_exportar = QPushButton("Exportar")
        self.btn_exportar.clicked.connect(self.exportar_datos)
        self.toolbar.addWidget(self.btn_exportar)
        
        # Añadir el botón de importar a la barra de herramientas
        self.btn_importar = QPushButton("Importar")
        self.btn_importar.clicked.connect(self.importar_datos)
        self.toolbar.addWidget(self.btn_importar)

        # Crear una barra de herramientas adicional para el botón de mostrar/ocultar
        self.toggle_toolbar = QToolBar("Toggle Toolbar")
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.toggle_toolbar)

        # Añadir un botón de icono para mostrar/ocultar la barra de herramientas
        self.toggle_toolbar_button = QPushButton()
        self.toggle_toolbar_button.setIcon(QIcon("/home/gonzapython/Documentos/Agenda_qt/iconos/tool_icon.png"))
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
        self.btn_alarma.clicked.connect(self.mostrar_alarma)

    def cargar_eventos(self):
        """Carga los eventos desde la base de datos"""
        eventos_db = self.db.obtener_eventos()
        self.eventos.clear()
        for evento in eventos_db:
            fecha_hora = datetime.strptime(evento[1], '%Y-%m-%d %H:%M:%S')
            self.eventos.append(Evento(evento[0], fecha_hora, evento[2]))
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
            self.alarma.actualizar_lista_tareas()
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
                self.alarma.actualizar_lista_tareas()
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
            respuesta = QMessageBox.question(self, "Confirmación", "¿Estás seguro de que deseas eliminar este evento?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if respuesta == QMessageBox.StandardButton.Yes:
                evento = self.eventos[selected_row]
                try:
                    self.db.eliminar_evento(evento_id=evento.id)
                    del self.eventos[selected_row]
                    self.actualizar_tabla_inmediata(evento, "eliminar")
                    self.alarma.actualizar_lista_tareas()
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Ocurrió un error al eliminar el evento: {str(e)}")
        else:
            QMessageBox.warning(self, "Advertencia", "Selecciona un evento para eliminar")

    @pyqtSlot()
    def mostrar_alarma(self):
        self.alarma.show()

    @pyqtSlot()
    def mostrar_contactos(self):
        self.contactos_window = ContactosWindow(self.db, self.user)  # Pasar el usuario actual
        self.contactos_window.exec()

    @pyqtSlot()
    def mostrar_compras(self):
        self.compras_window = ComprasWindow(self.db, self.user)  # Pasar el usuario actual
        self.compras_window.exec()



    @pyqtSlot()
    def gestionar_usuarios(self):
        # Obtener el rol del usuario actual desde alguna parte de tu aplicación
        rol_usuario_actual = self.user[1]  # Asegúrate de tener esta información disponible

        # Solicitar la contraseña del administrador
        intentos_fallidos = 0

        if self.bloqueado_hasta and time.time() < self.bloqueado_hasta:
            tiempo_restante = int(self.bloqueado_hasta - time.time())
            QMessageBox.warning(None, "Acceso Bloqueado", f"Acceso bloqueado. Intenta de nuevo en {tiempo_restante} segundos.")
            return

        while intentos_fallidos < 3:
            admin_password, ok = QInputDialog.getText(None, "Contraseña de Administrador", "Ingresa la contraseña del administrador:", QLineEdit.EchoMode.Password)
            if not ok or not admin_password:
                return  # Cierra la ventana si no se proporciona la contraseña

            # Verificar la contraseña del administrador
            if self.db.verificar_contrasena_admin(admin_password):
                self.gestionar_usuarios_window = GestionarUsuariosWindow(self.db, rol_usuario_actual)
                self.gestionar_usuarios_window.exec()
                return

            intentos_fallidos += 1
            QMessageBox.warning(None, "Error", "Contraseña de administrador incorrecta.")
            
            if intentos_fallidos >= 3:
                self.bloqueado_hasta = time.time() + 480  # Bloquear por 8 minutos
                QMessageBox.warning(None, "Error", "Ha excedido el número máximo de intentos. Acceso bloqueado por 8 minutos.")
                return  # Deshabilita el campo de entrada de la contraseña

        # Si se alcanzan los intentos fallidos, deshabilitar el campo de entrada de la contraseña
        if intentos_fallidos >= 3:
            self.bloqueado_hasta = time.time() + 480  # Bloquear por 8 minutos
            QMessageBox.warning(None, "Error", "Ha excedido el número máximo de intentos. Acceso bloqueado por 8 minutos.")
     
        
         
         
    @pyqtSlot()
    def exportar_datos(self):
        """Exporta los datos a un archivo seleccionado por el usuario"""
        archivo, _ = QFileDialog.getSaveFileName(self, "Guardar Archivo", "", "CSV Files (*.csv);;JSON Files (*.json);;XML Files (*.xml)")
        if archivo:
            if archivo.endswith('.csv'):
                self.exportar_csv(archivo)
            elif archivo.endswith('.json'):
                self.exportar_json(archivo)
            elif archivo.endswith('.xml'):
                self.exportar_xml(archivo)
                
                
    @pyqtSlot()
    def importar_datos(self):
        """Importa los datos desde un archivo seleccionado por el usuario"""
        archivo, _ = QFileDialog.getOpenFileName(self, "Abrir Archivo", "", "CSV Files (*.csv);;JSON Files (*.json);;XML Files (*.xml)")
        if archivo:
            if archivo.endswith('.csv'):
                self.importar_csv(archivo)
            elif archivo.endswith('.json'):
                self.importar_json(archivo)
            elif archivo.endswith('.xml'):
                self.importar_xml(archivo)
    

    def exportar_csv(self, archivo):
        """Exporta los datos a un archivo CSV"""
        with open(archivo, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["ID", "Fecha", "Hora", "Descripción"])
            for evento in self.eventos:
                writer.writerow([evento.id, evento.fecha_hora.strftime('%Y-%m-%d'), evento.fecha_hora.strftime('%H:%M'), evento.descripcion])

    def importar_csv(self, archivo):
        """Importa los datos desde un archivo CSV"""
        with open(archivo, 'r') as file:
            reader = csv.reader(file)
            next(reader)  # Saltar la cabecera
            for row in reader:
                fecha_hora = datetime.strptime(f"{row[1]} {row[2]}", '%Y-%m-%d %H:%M')
                self.db.agregar_evento(row[1], row[2], row[3])
                nuevo_evento_id = self.db.obtener_eventos()[-1][0]
                nuevo_evento = Evento(nuevo_evento_id, fecha_hora, row[3])
                self.eventos.append(nuevo_evento)
            self.actualizar_tabla()

    def exportar_json(self, archivo):
        """Exporta los datos a un archivo JSON"""
        eventos = [{"id": evento.id, "fecha": evento.fecha_hora.strftime('%Y-%m-%d'), "hora": evento.fecha_hora.strftime('%H:%M'), "descripcion": evento.descripcion} for evento in self.eventos]
        with open(archivo, 'w') as file:
            json.dump(eventos, file, indent=4)

    def importar_json(self, archivo):
        """Importa los datos desde un archivo JSON"""
        with open(archivo, 'r') as file:
            eventos = json.load(file)
            for evento in eventos:
                fecha_hora = datetime.strptime(f"{evento['fecha']} {evento['hora']}", '%Y-%m-%d %H:%M')
                self.db.agregar_evento(evento['fecha'], evento['hora'], evento['descripcion'])
                nuevo_evento_id = self.db.obtener_eventos()[-1][0]
                nuevo_evento = Evento(nuevo_evento_id, fecha_hora, evento['descripcion'])
                self.eventos.append(nuevo_evento)
            self.actualizar_tabla()

    def exportar_xml(self, archivo):
        """Exporta los datos a un archivo XML"""
        root = ET.Element("eventos")
        for evento in self.eventos:
            evento_element = ET.SubElement(root, "evento")
            ET.SubElement(evento_element, "id").text = str(evento.id)
            ET.SubElement(evento_element, "fecha").text = evento.fecha_hora.strftime('%Y-%m-%d')
            ET.SubElement(evento_element, "hora").text = evento.fecha_hora.strftime('%H:%M')
            ET.SubElement(evento_element, "descripcion").text = evento.descripcion
        tree = ET.ElementTree(root)
        tree.write(archivo)

    def importar_xml(self, archivo):
        """Importa los datos desde un archivo XML"""
        tree = ET.parse(archivo)
        root = tree.getroot()
        for evento_element in root.findall('evento'):
            fecha_hora = datetime.strptime(f"{evento_element.find('fecha').text} {evento_element.find('hora').text}", '%Y-%m-%d %H:%M')
            self.db.agregar_evento(evento_element.find('fecha').text, evento_element.find('hora').text, evento_element.find('descripcion').text)
            nuevo_evento_id = self.db.obtener_eventos()[-1][0]
            nuevo_evento = Evento(nuevo_evento_id, fecha_hora, evento_element.find('descripcion').text)
            self.eventos.append(nuevo_evento)
        self.actualizar_tabla()

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
