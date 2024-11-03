from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QHBoxLayout, QMessageBox,
    QComboBox, QSpinBox
)
from PyQt6.QtCore import Qt, QRegularExpression
from PyQt6.QtGui import QRegularExpressionValidator
import re
from models.database import Database

class ContactosWindow(QDialog):
    def __init__(self, db: Database):
        super().__init__()
        self.db = db
        self.page_size = 10  # Cantidad de registros por página
        self.current_page = 1
        self.total_pages = 1
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Contactos")
        self.setGeometry(150, 150, 800, 600)
        
        self.layout = QVBoxLayout()
        
        # Sección de búsqueda
        self.search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar contactos...")
        self.search_input.textChanged.connect(self.buscar_contactos)
        self.search_by = QComboBox()
        self.search_by.addItems(["Nombre", "Teléfono", "Email", "Documento"])
        self.search_layout.addWidget(self.search_input)
        self.search_layout.addWidget(self.search_by)
        self.layout.addLayout(self.search_layout)

        # Campos de entrada con validación
        self.nombre_label = QLabel("Nombre:")
        self.nombre_input = QLineEdit()
        
        self.telefono_label = QLabel("Teléfono:")
        self.telefono_input = QLineEdit()
        telefono_regex = QRegularExpression(r'^\+?[0-9]{6,15}$')
        telefono_validator = QRegularExpressionValidator(telefono_regex)
        self.telefono_input.setValidator(telefono_validator)
        
        self.email_label = QLabel("Correo Electrónico:")
        self.email_input = QLineEdit()
        
        self.documento_label = QLabel("Documento:")
        self.documento_input = QLineEdit()
        
        for widget in [self.nombre_label, self.nombre_input,
                      self.telefono_label, self.telefono_input,
                      self.email_label, self.email_input,
                      self.documento_label, self.documento_input]:
            self.layout.addWidget(widget)

        # Botones principales
        self.buttons_layout = QHBoxLayout()
        
        self.btn_agregar = QPushButton("Agregar Contacto")
        self.btn_agregar.clicked.connect(self.agregar_contacto)
        
        self.btn_editar = QPushButton("Editar")
        self.btn_editar.clicked.connect(self.editar_contacto)
        
        self.btn_eliminar = QPushButton("Eliminar")
        self.btn_eliminar.clicked.connect(self.eliminar_contacto)
        
        for btn in [self.btn_agregar, self.btn_editar, self.btn_eliminar]:
            self.buttons_layout.addWidget(btn)
        
        self.layout.addLayout(self.buttons_layout)

        # Tabla de contactos
        self.tabla_contactos = QTableWidget()
        self.tabla_contactos.setColumnCount(5)
        self.tabla_contactos.setHorizontalHeaderLabels(
            ["ID", "Nombre", "Teléfono", "Correo Electrónico", "Documento"]
        )
        self.tabla_contactos.setColumnHidden(0, True)
        self.tabla_contactos.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla_contactos.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tabla_contactos.clicked.connect(self.tabla_contactos_clicked)
        self.tabla_contactos.horizontalHeader().sectionClicked.connect(self.ordenar_tabla)
        self.layout.addWidget(self.tabla_contactos)

        # Ajustar el ancho de la columna del correo electrónico
        self.tabla_contactos.setColumnWidth(3, 200)  # Ajusta el valor según sea necesario

        # Controles de paginación
        self.pagination_layout = QHBoxLayout()
        
        self.btn_prev = QPushButton("Anterior")
        self.btn_prev.clicked.connect(self.pagina_anterior)
        
        self.page_label = QLabel("Página 1 de 1")
        
        self.btn_next = QPushButton("Siguiente")
        self.btn_next.clicked.connect(self.pagina_siguiente)
        
        self.page_size_spin = QSpinBox()
        self.page_size_spin.setRange(5, 100)
        self.page_size_spin.setValue(self.page_size)
        self.page_size_spin.valueChanged.connect(self.cambiar_tamano_pagina)
        
        for widget in [self.btn_prev, self.page_label, 
                      self.btn_next, QLabel("Registros por página:"), 
                      self.page_size_spin]:
            self.pagination_layout.addWidget(widget)
        
        self.layout.addLayout(self.pagination_layout)
        
        self.setLayout(self.layout)
        self.cargar_contactos()

    def validar_email(self, email):
        """Valida el formato del correo electrónico"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    def buscar_contactos(self):
        """Realiza la búsqueda de contactos según el criterio seleccionado"""
        texto = self.search_input.text().lower()
        criterio = self.search_by.currentText()
        
        for row in range(self.tabla_contactos.rowCount()):
            mostrar = False
            if criterio == "Nombre":
                col = 1
            elif criterio == "Teléfono":
                col = 2
            elif criterio == "Email":
                col = 3
            else:  # Documento
                col = 4
                
            item = self.tabla_contactos.item(row, col)
            if item and texto in item.text().lower():
                mostrar = True
                
            self.tabla_contactos.setRowHidden(row, not mostrar)

    def ordenar_tabla(self, column_index):
        """Ordena la tabla por la columna seleccionada"""
        self.tabla_contactos.sortItems(column_index)

    def cargar_contactos(self):
        """Carga los contactos desde la base de datos"""
        contactos = self.db.obtener_contactos()
        self.tabla_contactos.setRowCount(0)
        for contacto in contactos:
            row_position = self.tabla_contactos.rowCount()
            self.tabla_contactos.insertRow(row_position)
            
            # Agregar una columna oculta para el ID
            id_item = QTableWidgetItem(str(contacto[0]))
            id_item.setFlags(Qt.ItemFlag.ItemIsEnabled)
            self.tabla_contactos.setItem(row_position, 0, id_item)
            
            # Agregar los demás campos
            self.tabla_contactos.setItem(row_position, 1, QTableWidgetItem(contacto[1]))
            self.tabla_contactos.setItem(row_position, 2, QTableWidgetItem(contacto[2]))
            self.tabla_contactos.setItem(row_position, 3, QTableWidgetItem(contacto[3]))
            self.tabla_contactos.setItem(row_position, 4, QTableWidgetItem(contacto[4]))

    def tabla_contactos_clicked(self):
        """Llena los campos de entrada con los datos del contacto seleccionado"""
        selected_items = self.tabla_contactos.selectedItems()
        if len(selected_items) >= 4:  # Verificar solo los 4 elementos visibles
            # Verificar que todos los elementos seleccionados no sean None
            nombre_item = selected_items[0]
            telefono_item = selected_items[1]
            email_item = selected_items[2]
            documento_item = selected_items[3]
    
            missing_fields = []
            if not nombre_item:
                missing_fields.append("Nombre")
            if not telefono_item:
                missing_fields.append("Teléfono")
            if not email_item:
                missing_fields.append("Correo Electrónico")
            if not documento_item:
                missing_fields.append("Documento")
    
            if missing_fields:
                QMessageBox.warning(self, "Advertencia", f"No se pudo obtener los siguientes datos del contacto seleccionado: {', '.join(missing_fields)}")
            else:
                self.nombre_input.setText(nombre_item.text())
                self.telefono_input.setText(telefono_item.text())
                self.email_input.setText(email_item.text())
                self.documento_input.setText(documento_item.text())
        else:
            QMessageBox.warning(self, "Advertencia", "No se pudo obtener todos los datos del contacto seleccionado.")
        
    def agregar_contacto(self):
        """Agrega un nuevo contacto a la base de datos"""
        nombre = self.nombre_input.text()
        telefono = self.telefono_input.text()
        email = self.email_input.text()
        documento = self.documento_input.text()
        
        if nombre and telefono and email and documento:
            if self.db.contacto_duplicado(email, documento):
                QMessageBox.warning(self, "Advertencia", "Este contacto ya está en la base de datos.")
                return

            try:
                self.db.agregar_contacto(nombre, telefono, email, documento)
                self.cargar_contactos()
                self.nombre_input.clear()
                self.telefono_input.clear()
                self.email_input.clear()
                self.documento_input.clear()
                QMessageBox.information(self, "Éxito", "Contacto agregado correctamente.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al agregar contacto: {e}")
        else:
            QMessageBox.warning(self, "Advertencia", "Todos los campos son obligatorios.")

    def editar_contacto(self):
        """Edita un contacto existente en la base de datos"""
        try:
            selected_row = self.tabla_contactos.currentRow()
            if selected_row >= 0:
                contacto_id_item = self.tabla_contactos.item(selected_row, 0)
                if contacto_id_item is None:
                    QMessageBox.warning(self, "Advertencia", "No se pudo obtener el ID del contacto seleccionado.")
                    return
                
                contacto_id = int(contacto_id_item.text())
                nombre = self.nombre_input.text()
                telefono = self.telefono_input.text()
                email = self.email_input.text()
                documento = self.documento_input.text()
                
                if nombre and telefono and email and documento:
                    self.db.editar_contacto(contacto_id, nombre, telefono, email, documento)
                    self.cargar_contactos()
                    self.nombre_input.clear()
                    self.telefono_input.clear()
                    self.email_input.clear()
                    self.documento_input.clear()
                    QMessageBox.information(self, "Éxito", "Contacto editado correctamente.")
                else:
                    QMessageBox.warning(self, "Advertencia", "Todos los campos son obligatorios.")
            else:
                QMessageBox.warning(self, "Advertencia", "Selecciona un contacto para editar.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al editar contacto: {e}")

    def eliminar_contacto(self):
        """Elimina un contacto de la base de datos"""
        try:
            selected_row = self.tabla_contactos.currentRow()
            if selected_row >= 0:
                contacto_id_item = self.tabla_contactos.item(selected_row, 0)
                if contacto_id_item is None:
                    QMessageBox.warning(self, "Advertencia", "No se pudo obtener el ID del contacto seleccionado.")
                    return
                
                contacto_id = int(contacto_id_item.text())
                
                # Confirmación antes de eliminar
                respuesta = QMessageBox.question(
                    self, "Confirmación",
                    "¿Estás seguro de que deseas eliminar este contacto?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                
                if respuesta == QMessageBox.StandardButton.Yes:
                    self.db.eliminar_contacto(contacto_id)
                    self.cargar_contactos()
                    QMessageBox.information(self, "Éxito", "Contacto eliminado correctamente.")
            else:
                QMessageBox.warning(self, "Advertencia", "Selecciona un contacto para eliminar.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al eliminar contacto: {e}")

    def pagina_anterior(self):
        """Navega a la página anterior"""
        if self.current_page > 1:
            self.current_page -= 1
            self.cargar_contactos()

    def pagina_siguiente(self):
        """Navega a la página siguiente"""
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.cargar_contactos()

    def cambiar_tamano_pagina(self):
        """Cambia el tamaño de la página"""
        self.page_size = self.page_size_spin.value()
        self.cargar_contactos()

   