import csv
import json
import xml.etree.ElementTree as ET


def exportar_csv(eventos, nombre_archivo):
    """Exporta los eventos a un archivo CSV."""
    with open(nombre_archivo, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["ID", "Fecha", "Hora", "Descripción"])
        for evento in eventos:
            writer.writerow([evento.id, evento.fecha_hora.strftime('%Y-%m-%d'), evento.fecha_hora.strftime('%H:%M'), evento.descripcion])

def exportar_json(eventos, nombre_archivo):
    """Exporta los eventos a un archivo JSON."""
    datos = [
        {
            "id": evento.id,
            "fecha": evento.fecha_hora.strftime('%Y-%m-%d'),
            "hora": evento.fecha_hora.strftime('%H:%M'),
            "descripcion": evento.descripcion
        }
        for evento in eventos
    ]
    with open(nombre_archivo, 'w') as file:
        json.dump(datos, file, indent=4)

def exportar_xml(eventos, nombre_archivo):
    """Exporta los eventos a un archivo XML."""
    root = ET.Element("eventos")
    for evento in eventos:
        evento_element = ET.SubElement(root, "evento")
        ET.SubElement(evento_element, "id").text = str(evento.id)
        ET.SubElement(evento_element, "fecha").text = evento.fecha_hora.strftime('%Y-%m-%d')
        ET.SubElement(evento_element, "hora").text = evento.fecha_hora.strftime('%H:%M')
        ET.SubElement(evento_element, "descripcion").text = evento.descripcion
    tree = ET.ElementTree(root)
    tree.write(nombre_archivo)

def importar_csv(nombre_archivo):
    """Importa eventos desde un archivo CSV."""
    eventos = []
    with open(nombre_archivo, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            eventos.append({
                "fecha": row["Fecha"],
                "hora": row["Hora"],
                "descripcion": row["Descripción"]
            })
    return eventos

def importar_json(nombre_archivo):
    """Importa eventos desde un archivo JSON."""
    with open(nombre_archivo, 'r') as file:
        eventos = json.load(file)
    return eventos

def importar_xml(nombre_archivo):
    """Importa eventos desde un archivo XML."""
    tree = ET.parse(nombre_archivo)
    root = tree.getroot()
    eventos = []
    for evento_element in root.findall('evento'):
        eventos.append({
            "fecha": evento_element.find('fecha').text,
            "hora": evento_element.find('hora').text,
            "descripcion": evento_element.find('descripcion').text
        })
    return eventos
