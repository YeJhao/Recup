"""
semantic_generator.py

Generador de datos RDF/Turtle basados en Zaguan

Usa: python SemanticGenerator.py -rdf coleccion.ttl -docs carpeta_xml
"""

from rdflib import Graph, Namespace, Literal, URIRef, BNode
from rdflib.namespace import RDF, RDFS, XSD, FOAF
import uuid
import datetime
import random

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
def new_uri(prefix="zag", kind="resource"):
    uid = str(uuid.uuid4())
    return ZAG[f"{kind}/{uid}"]

# Creación de clases
def createPersona(g: Graph, name: str, id: str):
    person_uri = URIRef(new_uri(kind="persona"))
    g.add((person_uri, RDF.type, ZAGUAN.persona))
    g.add((person_uri, ZAGUAN.nombrePersona, Literal(name, datatype=XSD.string)))
    g.add((person_uri, FOAF.page, URIRef(id)))
    return person_uri

def createTema(g: Graph, nombre: str):
    tema_uri = URIRef(new_uri(kind="tema"))
    g.add((tema_uri, RDF.type, ZAGUAN.Tema))
    g.add((tema_uri, ZAGUAN.nombreTema, Literal(nombre, datatype=XSD.string)))
    return tema_uri

def createEntidad(g: Graph, nombre: str):
    entidad_uri = URIRef(new_uri(kind="entidad"))
    g.add((entidad_uri, RDF.type, ZAGUAN.Entidad))
    g.add((entidad_uri, ZAGUAN.nombreEntidad, Literal(nombre, datatype=XSD.string)))
    return entidad_uri

def createDocumento(
    g: Graph,
    title: str,
    date: datetime.date,
    description: str = None,
    language: str = "es",
    rights: str = None,
    relation: str = None,
    subject_tema_uri: URIRef = None,
    publisher_entidad_uri: URIRef = None,
    authors: list = None,
    contributors: list = None,
):
    doc_uri = URIRef(new_uri(kind="documento"))
    g.add((doc_uri, RDF.type, ZAGUAN.documento))
    g.add((doc_uri, ZAGUAN.title, Literal(title, datatype=XSD.string)))
    g.add((doc_uri, ZAGUAN.date, Literal(date.isoformat(), datatype=XSD.date)))
    if description:
        g.add((doc_uri, ZAGUAN.description, Literal(description, datatype=XSD.string)))
    if language:
        g.add((doc_uri, ZAGUAN.language, Literal(language, datatype=XSD.string)))
    if rights:
        g.add((doc_uri, ZAGUAN.rights, Literal(rights, datatype=XSD.string)))
    if relation:
        g.add((doc_uri, ZAGUAN.relation, Literal(relation, datatype=XSD.string)))
    if subject_tema_uri:
        g.add((doc_uri, ZAGUAN.subject, subject_tema_uri))
    if publisher_entidad_uri:
        g.add((doc_uri, ZAGUAN.publisher, publisher_entidad_uri))
    if authors:
        for a in authors:
            g.add((doc_uri, ZAGUAN.author, a))
    if contributors:
        for c in contributors:
            g.add((doc_uri, ZAGUAN.contributor, c))
    return doc_uri

# Inicialización del grafo
def createGraph():
    g = Graph()
    # bind de prefijos
    for pfx, ns in PREFIXES.items():
        g.bind(pfx, ns)
    # Declaraciones de clases y propiedades
    g.add((ZAGUAN.documento, RDF.type, RDFS.Class))
    g.add((ZAGUAN.persona, RDF.type, RDFS.Class))
    g.add((ZAGUAN.Tema, RDF.type, RDFS.Class))
    g.add((ZAGUAN.Entidad, RDF.type, RDFS.Class))
    # Declaración de propiedades
    for prop in ("title", "date", "description", "language", "rights", "relation", "subject", "publisher", "author", "contributor", "nombrePersona", "nombreTema", "nombreEntidad"):
        g.add((ZAGUAN[prop], RDF.type, RDF.Property))
    return g

def main()

if __name__ == "__main__":
    main()
