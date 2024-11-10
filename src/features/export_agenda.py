# aqui  las funciones o clases para exportar la agenda a csv , json, xml
# tambien se puede hacer para importar la agenda desde csv, json, xml
import csv
import json
import xml.etree.ElementTree as ET
from PyQt6.QtWidgets import QFileDialog, QMessageBox

def exportar_csv(datos, nombre_archivo):
    """Exporta los datos a un archivo CSV."""
    try:
        with open(nombre_archivo, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(datos)
        QMessageBox.information(None, "Exportación Exitosa", "Datos exportados a CSV correctamente.")
    except Exception as e:
        QMessageBox.critical(None, "Error", f"Error al exportar a CSV: {e}")

def exportar_json(datos, nombre_archivo):
    """Exporta los datos a un archivo JSON."""
    try:
        with open(nombre_archivo, 'w') as file:
            json.dump(datos, file, indent=4)
        QMessageBox.information(None, "Exportación Exitosa", "Datos exportados a JSON correctamente.")
    except Exception as e:
        QMessageBox.critical(None, "Error", f"Error al exportar a JSON: {e}")

def exportar_xml(datos, nombre_archivo):
    """Exporta los datos a un archivo XML."""
    try:
        root = ET.Element("root")
        for item in datos:
            elemento = ET.SubElement(root, "item")
            for key, value in item.items():
                subelemento = ET.SubElement(elemento, key)
                subelemento.text = str(value)
        tree = ET.ElementTree(root)
        tree.write(nombre_archivo)
        QMessageBox.information(None, "Exportación Exitosa", "Datos exportados a XML correctamente.")
    except Exception as e:
        QMessageBox.critical(None, "Error", f"Error al exportar a XML: {e}")

def importar_csv(nombre_archivo):
    """Importa datos desde un archivo CSV."""
    try:
        with open(nombre_archivo, 'r') as file:
            reader = csv.reader(file)
            datos = [row for row in reader]
        QMessageBox.information(None, "Importación Exitosa", "Datos importados desde CSV correctamente.")
        return datos
    except Exception as e:
        QMessageBox.critical(None, "Error", f"Error al importar desde CSV: {e}")
        return []

def importar_json(nombre_archivo):
    """Importa datos desde un archivo JSON."""
    try:
        with open(nombre_archivo, 'r') as file:
            datos = json.load(file)
        QMessageBox.information(None, "Importación Exitosa", "Datos importados desde JSON correctamente.")
        return datos
    except Exception as e:
        QMessageBox.critical(None, "Error", f"Error al importar desde JSON: {e}")
        return []

def importar_xml(nombre_archivo):
    """Importa datos desde un archivo XML."""
    try:
        tree = ET.parse(nombre_archivo)
        root = tree.getroot()
        datos = []
        for item in root.findall('item'):
            datos.append({child.tag: child.text for child in item})
        QMessageBox.information(None, "Importación Exitosa", "Datos importados desde XML correctamente.")
        return datos
    except Exception as e:
        QMessageBox.critical(None, "Error", f"Error al importar desde XML: {e}")
        return []

