from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QHBoxLayout, QMessageBox
)
from PyQt6.QtCore import Qt
from models.database import Database

class ComprasWindow(QDialog):
    def __init__(self, db: Database):
        super().__init__()
        self.db = db
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Compras")
        self.setGeometry(150, 150, 800, 600)
        
        self.layout = QVBoxLayout()
        
        # Campos de entrada
        self.nombre_label = QLabel("Nombre del Producto:")
        self.nombre_input = QLineEdit()
        
        self.cantidad_label = QLabel("Cantidad:")
        self.cantidad_input = QLineEdit()
        
        self.precio_label = QLabel("Precio:")
        self.precio_input = QLineEdit()
        
        for widget in [self.nombre_label, self.nombre_input,
                      self.cantidad_label, self.cantidad_input,
                      self.precio_label, self.precio_input]:
            self.layout.addWidget(widget)

        # Botones principales
        self.buttons_layout = QHBoxLayout()
        
        self.btn_agregar = QPushButton("Agregar Compra")
        self.btn_agregar.clicked.connect(self.agregar_compra)
        
        self.btn_editar = QPushButton("Editar")
        self.btn_editar.clicked.connect(self.editar_compra)
        
        self.btn_eliminar = QPushButton("Eliminar")
        self.btn_eliminar.clicked.connect(self.eliminar_compra)
        
        for btn in [self.btn_agregar, self.btn_editar, self.btn_eliminar]:
            self.buttons_layout.addWidget(btn)
        
        self.layout.addLayout(self.buttons_layout)

        # Tabla de compras
        self.tabla_compras = QTableWidget()
        self.tabla_compras.setColumnCount(4)
        self.tabla_compras.setHorizontalHeaderLabels(
            ["ID", "Nombre", "Cantidad", "Precio"]
        )
        self.tabla_compras.setColumnHidden(0, True)
        self.tabla_compras.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla_compras.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tabla_compras.clicked.connect(self.tabla_compras_clicked)
        self.layout.addWidget(self.tabla_compras)

        # Ajustar el ancho de las columnas
        self.tabla_compras.setColumnWidth(1, 200)  # Ajusta el valor según sea necesario
        self.tabla_compras.setColumnWidth(2, 200)  # Ajusta el valor según sea necesario
        self.tabla_compras.setColumnWidth(3, 200)  # Ajusta el valor según sea necesario

        self.setLayout(self.layout)
        self.cargar_compras()

    def cargar_compras(self):
        """Carga las compras desde la base de datos"""
        compras = self.db.obtener_compras()
        self.tabla_compras.setRowCount(0)
        for compra in compras:
            row_position = self.tabla_compras.rowCount()
            self.tabla_compras.insertRow(row_position)
            
            # Agregar una columna oculta para el ID
            id_item = QTableWidgetItem(str(compra[0]))
            id_item.setFlags(Qt.ItemFlag.ItemIsEnabled)
            self.tabla_compras.setItem(row_position, 0, id_item)
            
            # Agregar los demás campos
            self.tabla_compras.setItem(row_position, 1, QTableWidgetItem(compra[1]))
            self.tabla_compras.setItem(row_position, 2, QTableWidgetItem(compra[2]))
            self.tabla_compras.setItem(row_position, 3, QTableWidgetItem(compra[3]))

    def tabla_compras_clicked(self):
        """Llena los campos de entrada con los datos de la compra seleccionada"""
        selected_items = self.tabla_compras.selectedItems()
        if len(selected_items) >= 3:  # Verificar solo los 3 elementos visibles
            self.nombre_input.setText(selected_items[0].text())
            self.cantidad_input.setText(selected_items[1].text())
            self.precio_input.setText(selected_items[2].text())
        else:
            QMessageBox.warning(self, "Advertencia", "No se pudo obtener todos los datos de la compra seleccionada.")

    def agregar_compra(self):
        """Agrega una nueva compra a la base de datos"""
        nombre = self.nombre_input.text()
        cantidad = self.cantidad_input.text()
        precio = self.precio_input.text()
        
        if nombre and cantidad and precio:
            # Verificar si el producto ya existe
            if self.db.compra_duplicada(nombre):
                QMessageBox.warning(self, "Advertencia", "Este producto ya está en la base de datos.")
                return

            try:
                self.db.agregar_compra(nombre, cantidad, precio)
                self.cargar_compras()
                self.nombre_input.clear()
                self.cantidad_input.clear()
                self.precio_input.clear()
                QMessageBox.information(self, "Éxito", "Compra agregada correctamente.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al agregar compra: {e}")
        else:
            QMessageBox.warning(self, "Advertencia", "Todos los campos son obligatorios.")

    def editar_compra(self):
        """Edita una compra existente en la base de datos"""
        selected_row = self.tabla_compras.currentRow()
        if selected_row >= 0:
            compra_id_item = self.tabla_compras.item(selected_row, 0)
            if compra_id_item is None:
                QMessageBox.warning(self, "Advertencia", "No se pudo obtener el ID de la compra seleccionada.")
                return
            
            compra_id = int(compra_id_item.text())
            nombre = self.nombre_input.text()
            cantidad = self.cantidad_input.text()
            precio = self.precio_input.text()
            
            if nombre and cantidad and precio:
                try:
                    self.db.editar_compra(compra_id, nombre, cantidad, precio)
                    self.cargar_compras()
                    self.nombre_input.clear()
                    self.cantidad_input.clear()
                    self.precio_input.clear()
                    QMessageBox.information(self, "Éxito", "Compra editada correctamente.")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Error al editar compra: {e}")
            else:
                QMessageBox.warning(self, "Advertencia", "Todos los campos son obligatorios.")
        else:
            QMessageBox.warning(self, "Advertencia", "Selecciona una compra para editar.")

    def eliminar_compra(self):
        """Elimina una compra de la base de datos"""
        selected_row = self.tabla_compras.currentRow()
        if selected_row >= 0:
            compra_id_item = self.tabla_compras.item(selected_row, 0)
            if compra_id_item is None:
                QMessageBox.warning(self, "Advertencia", "No se pudo obtener el ID de la compra seleccionada.")
                return
            
            compra_id = int(compra_id_item.text())
            
            respuesta = QMessageBox.question(
                self, "Confirmación",
                "¿Estás seguro de que deseas eliminar esta compra?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if respuesta == QMessageBox.StandardButton.Yes:
                try:
                    self.db.eliminar_compra(compra_id)
                    self.cargar_compras()
                    QMessageBox.information(self, "Éxito", "Compra eliminada correctamente.")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Error al eliminar compra: {e}")
        else:
            QMessageBox.warning(self, "Advertencia", "Selecciona una compra para eliminar.")