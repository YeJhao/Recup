"""
SemanticSearcher.py

Búsqueda semántica utilizando SPARQL en un endpoint RDF.

Uso: python SemanticSearcher.py -infoNeeds <infoNeedsFile> -output <resultsFile>
"""


import sys
import xml.etree.ElementTree as ET
from SPARQLWrapper import SPARQLWrapper, JSON

def search(info_needs_file, output_file, sparql_endpoint="http://localhost:3030/datasetExample/query"):
    tree = ET.parse(info_needs_file)
    root = tree.getroot()

    results_lines = []

    sparql = SPARQLWrapper(sparql_endpoint)
    sparql.setReturnFormat(JSON)

    for need in root.findall("informationNeed"):
        identifier = need.find("identifier").text.strip()
        query_text = need.find("text").text.strip()

        # Ejecuta la consulta SPARQL
        sparql.setQuery(query_text)
        try:
            response = sparql.query().convert()
            for result in response["results"]["bindings"]:
                doc_uri = result["doc"]["value"]
                results_lines.append(f"{identifier}\t{doc_uri}")
        except Exception as e:
            print(f"Error al ejecutar la consulta {identifier}: {e}")

    # Escribe los resultados
    with open(output_file, "w", encoding="utf-8") as f:
        for line in results_lines:
            f.write(line + "\n")

if __name__ == "__main__":
    # Valores por defecto
    need_file = './necesidadesInformacionElegidas.xml'
    output_file = './semanticResults111.txt'
    i = 1
    while i < len(sys.argv):
        if sys.argv[i] == '-infoNeeds':
            need_file = sys.argv[i + 1]
            i = i + 1
        elif sys.argv[i] == '-output':
            output_file = sys.argv[i + 1]
            i = i + 1
        i = i + 1

    search(need_file, output_file)
