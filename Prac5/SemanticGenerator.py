"""
semantic_generator.py

Generador de datos RDF/Turtle basados en Zaguan

Usa: python SemanticGenerator.py -rdf <rdfPath> -docs <docsPath>
"""

from rdflib import Graph, Namespace, Literal, URIRef, BNode
from rdflib.namespace import RDF, RDFS, XSD, FOAF

import sys
import os
import re

import uuid
import datetime
import random

import xml.etree.ElementTree as ET

# namespaces
ZAGUAN = Namespace("http://zaguan.unizar.es/ontologia#")
ZAG = Namespace("http://example.org/zaguan/")
# Prefijos
PREFIXES = {
    "zaguan": ZAGUAN,
    "zag": ZAG,
    "rdf": RDF,
    "rdfs": RDFS,
    "xsd": XSD,
    "foaf": FOAF
}

# Generador de URIs únicas
def new_uri(kind="resource", value=None):
    if value:
        # Normalizamos, minúsculas, sin espacios, ni caracteres especiales
        value = value.strip().lower()
        value = value.replace(" ", "_")
        # Eliminamos caracteres no alfanuméricos excepto guiones y guiones bajos
        value = re.sub(r"[^a-z0-9_\-]", "", value)

        return ZAG[f"{kind}/{value}"]
    
    uid = str(uuid.uuid4())
    return ZAG[f"{kind}/{uid}"]

# Creación de clases

# Crea la URI de una persona y la añade al grafo
def createPersona(g: Graph, name: str):
    person_uri = URIRef(new_uri(kind="persona", value=name))
    g.add((person_uri, RDF.type, ZAGUAN.persona))
    g.add((person_uri, ZAGUAN.nombrePersona, Literal(name)))

    return person_uri

# Crea la URI de un tema y la añade al grafo
def createTema(g: Graph, name: str):
    tema_uri = URIRef(new_uri(kind="tema", value=name))
    g.add((tema_uri, RDF.type, ZAGUAN.Tema))
    g.add((tema_uri, ZAGUAN.nombreTema, Literal(name)))

    return tema_uri

# Crea la URI de un publisher y la añade al grafo
def createEntidad(g: Graph, name: str):
    entidad_uri = URIRef(new_uri(kind="entidad", value=name))
    g.add((entidad_uri, RDF.type, ZAGUAN.Entidad))
    g.add((entidad_uri, ZAGUAN.nombreEntidad, Literal(name)))

    return entidad_uri

def createGraph(input_path, output_path, schema_path="esquema.ttl"):
    # Leer del input_path
    # Crear grafo en output_path
    g = Graph()

    g.parse(schema_path, format="turtle")

    # Definimos prefijos para el grafo
    for pfx, ns in PREFIXES.items():
        g.bind(pfx, ns)

    # Diccionarios para evitar duplicados, solo estos tres porque los demás son literales (documentos únicos)
    temas_dict = {}
    personas_dict = {}
    entidades_dict = {}

    if (os.path.exists(input_path)):
        for file in sorted(os.listdir(input_path)):
            if file.endswith('.xml'):
                print(f"Procesando {file}")  # Debug o mirar el progreso

                file_path = os.path.join(input_path, file)

                tree = ET.parse(file_path)
                root = tree.getroot()

                namespaces = { 'dc': 'http://purl.org/dc/elements/1.1/' }

                path_element = root.find('.//dc:identifier', namespaces)

                identifier_url = path_element.text.strip()

                # Extraer el número final de la URL
                doc_id = identifier_url.split("/")[-1]

                # Tenemos la URI del documento
                doc_uri = new_uri(kind="documento", value=doc_id)

                type_element = root.find('.//dc:type', namespaces)

                if type_element.text == "TESIS":
                    g.add((doc_uri, RDF.type, ZAGUAN.tesis))
                elif type_element.text == "TAZ-PFC":
                    g.add((doc_uri, RDF.type, ZAGUAN.PFC))
                elif type_element.text == "TAZ-TFG":
                    g.add((doc_uri, RDF.type, ZAGUAN.TFG))
                elif type_element.text == "TAZ-TFM":
                    g.add((doc_uri, RDF.type, ZAGUAN.TFM))

                g.add((doc_uri, RDF.type, ZAGUAN.documento))

                title_element = root.find('.//dc:title', namespaces)
                
                if title_element is not None:
                    g.add((doc_uri, ZAGUAN.title, Literal(title_element.text)))

                date_element = root.find('.//dc:date', namespaces)

                if date_element is not None:
                    g.add((doc_uri, ZAGUAN.date, Literal(date_element.text, datatype=XSD.gYear)))

                description_element = root.find('.//dc:description', namespaces)

                if description_element is not None:
                    g.add((doc_uri, ZAGUAN.description, Literal(description_element.text)))

                language_element = root.find('.//dc:language', namespaces)
                
                if language_element is not None:
                    g.add((doc_uri, ZAGUAN.language, Literal(language_element.text)))

                rights_element = root.find('.//dc:rights', namespaces)

                if rights_element is not None:
                    g.add((doc_uri, ZAGUAN.rights, Literal(rights_element.text)))

                relation_element = root.find('.//dc:relation', namespaces)

                if relation_element is not None:
                    g.add((doc_uri, ZAGUAN.relation, Literal(relation_element.text)))

                autor_element = root.find('.//dc:creator', namespaces)

                if autor_element is not None and not autor_element.text.isdigit():
                    if autor_element.text not in personas_dict:
                        creator_uri = createPersona(g, autor_element.text)
                        personas_dict[autor_element.text] = creator_uri

                    g.add((doc_uri, ZAGUAN.author, personas_dict[autor_element.text]))

                # Para todos los contribuidores
                for contributor_element in root.findall('.//dc:contributor', namespaces):
                    if not contributor_element.text or contributor_element.text.isdigit():
                        continue
                    
                    if contributor_element.text not in personas_dict:
                        contributor_uri = createPersona(g, contributor_element.text)
                        personas_dict[contributor_element.text] = contributor_uri

                    g.add((doc_uri, ZAGUAN.contributor, personas_dict[contributor_element.text]))
                
                # Para los temas
                for subject_element in root.findall('.//dc:subject', namespaces):
                    if not subject_element.text:
                        continue

                    if subject_element.text not in temas_dict:
                        tema_uri = createTema(g, subject_element.text)
                        temas_dict[subject_element.text] = tema_uri

                    g.add((doc_uri, ZAGUAN.subject, temas_dict[subject_element.text]))

                publisher_element = root.find('.//dc:publisher', namespaces)

                if publisher_element is not None:
                    if publisher_element.text not in entidades_dict:
                        entidad_uri = createEntidad(g, publisher_element.text)
                        entidades_dict[publisher_element.text] = entidad_uri

                    g.add((doc_uri, ZAGUAN.publisher, entidades_dict[publisher_element.text]))

        # Guardar el grafo en formato Turtle
        os.makedirs(output_path, exist_ok=True)

        g.serialize(destination=os.path.join(output_path, "rdfGraph.ttl"), format="turtle")
    else:
        print(f"{input_path} no encontrada") 

if __name__ == "__main__":
    # Valores por defecto
    xml_folder = '../recordsdc'
    output_dir = './rdf'
    i = 1
    while i < len(sys.argv):
        if sys.argv[i] == '-rdf':
            output_dir = sys.argv[i + 1]
            i = i + 1
        elif sys.argv[i] == '-docs':
            xml_folder = sys.argv[i + 1]
            i = i + 1
        i = i + 1
    
    # Crear el fichero con el grafo RDF-Turtle
    createGraph(xml_folder, output_dir)
