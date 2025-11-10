"""
    SemanticGenerator.py
    Genera un grafo RDF/Turtle a partir de una colección XML (Zaguán Unizar)
    Uso:
    python SemanticGenerator.py -rdf salida.ttl -docs ./coleccion/
"""

import os
import argparse
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF, RDFS, DC
import xml.etree.ElementTree as ET

# Namespaces
ZAG = Namespace("http://zaguan.unizar.es/schema#")
BASE = Namespace("http://zaguan.unizar.es/resource/")


def parse_zaguan_xml(file_path, model):
    tree = ET.parse(file_path)
    root = tree.getroot()

    ids = [el.text for el in root.findall(".//{http://purl.org/dc/elements/1.1/}identifier")]
    if not ids:
        return
    doc_uri = URIRef(ids[0])
    model.add((doc_uri, RDF.type, ZAG.Tesis))

    # Campos de texto
    mappings = {
        "title": ZAG.titulo,
        "description": ZAG.descripcion,
        "date": ZAG.fechaPublicacion,
        "language": ZAG.lengua,
        "type": ZAG.tipoDocumento,
        "rights": ZAG.derechos
    }

    for tag, prop in mappings.items():
        for el in root.findall(f".//{{http://purl.org/dc/elements/1.1/}}{tag}"):
            if el.text:
                model.add((doc_uri, prop, Literal(el.text.strip())))

    # Autor
    for el in root.findall(".//{http://purl.org/dc/elements/1.1/}creator"):
        if el.text:
            autor_uri = URIRef(BASE + "autor/" + el.text.replace(" ", "_"))
            model.add((autor_uri, RDF.type, ZAG.Autor))
            model.add((autor_uri, ZAG.nombre, Literal(el.text)))
            model.add((doc_uri, ZAG.autor, autor_uri))

    # Colaboradores
    for el in root.findall(".//{http://purl.org/dc/elements/1.1/}contributor"):
        if el.text:
            col_uri = URIRef(BASE + "colaborador/" + el.text.replace(" ", "_"))
            model.add((col_uri, RDF.type, ZAG.Colaborador))
            model.add((col_uri, ZAG.nombre, Literal(el.text)))
            model.add((doc_uri, ZAG.colaborador, col_uri))

    # Temas
    for el in root.findall(".//{http://purl.org/dc/elements/1.1/}subject"):
        if el.text:
            model.add((doc_uri, ZAG.tema, Literal(el.text.strip())))

    # Publisher
    for el in root.findall(".//{http://purl.org/dc/elements/1.1/}publisher"):
        if el.text:
            inst_uri = URIRef(BASE + "inst/" + el.text.replace(" ", "_"))
            model.add((inst_uri, RDF.type, ZAG.Institucion))
            model.add((inst_uri, ZAG.nombre, Literal(el.text)))
            model.add((doc_uri, ZAG.editor, inst_uri))

    # Relaciones
    for el in root.findall(".//{http://purl.org/dc/elements/1.1/}relation"):
        if el.text:
            model.add((doc_uri, ZAG.relacion, URIRef(el.text.strip())))

def main():
    parser = argparse.ArgumentParser(description="Generador semántico para la colección Zaguán-Unizar")
    parser.add_argument("-rdf", required=True, help="Ruta del archivo de salida RDF/Turtle")
    parser.add_argument("-docs", required=True, help="Ruta del directorio con los XML de entrada")
    args = parser.parse_args()

    docs_path = args.docs
    rdf_path = args.rdf

    # Crear grafo y enlazar namespaces
    g = Graph()
    g.bind("zag", ZAG)
    g.bind("dc", DC)
    g.bind("rdfs", RDFS)

    # Recorrer todos los XML del directorio
    for filename in os.listdir(docs_path):
        if filename.lower().endswith(".xml"):
            file_path = os.path.join(docs_path, filename)
            print(f"Procesando: {file_path}")
            parse_zaguan_xml(file_path, g)

    # Guardar el grafo resultante
    g.serialize(destination=rdf_path, format="turtle")
    print(f"\n✅ Grafo RDF generado correctamente en: {rdf_path}")

# ------------------------------------------------------
if __name__ == "__main__":
    main()
