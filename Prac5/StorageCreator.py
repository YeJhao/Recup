"""
StorageCreator.py

Crea un dataset en Fuseki y carga datos RDF desde un fichero Turtle.

Uso: python StorageCreator.py -conf <confPath> -rdf <rdfPath>
"""

import sys
import requests, time

# URL de Fuseki admin
FUSEKI_HOST = 'http://localhost:3030'
ADMIN_USER = 'admin'
ADMIN_PASS = 'admin'

# Crea un almacén RDF nuevo en el servicio de FUSEKI
# La configuración de dicho almacén es la indicada en el fichero config_file
def datasetCreation(config_file):
    with open(config_file, 'rb') as f:
        response = requests.post(
            f"{FUSEKI_HOST}/$/datasets",
            files={
                "config": (config_file, f, "text/turtle")
            },
            auth=(ADMIN_USER, ADMIN_PASS)
        )
    return response

# Carga un fichero RDF en el almacén que se ha creado. El rdf tiene una estructura con los índices ya creados.
def rdfLoad(dataset_name, rdf_file):
    with open(rdf_file, "rb") as f:
        response = requests.post(
            f"{FUSEKI_HOST}/{dataset_name}/data",
            data=f,
            headers={"Content-Type": "text/turtle"},
            auth=(ADMIN_USER, ADMIN_PASS)
        )
    return response

# Crea un almacén con el nombre y configuración indicada.
def fusekiConfiguration(dataset_name, config_file, rdf_file):
    response = datasetCreation(config_file)
    if response.status_code == 200:
        time.sleep(2) # Esperamos a que el servicio se actualice correctamente
        response = rdfLoad(dataset_name, rdf_file)
        if response.status_code == 200:
            print(f" Archivo '{rdf_file}' cargado")
        else:
            print(f' Error cargando archivo: {response.status_code} - {response.text}')
    else:
        print(f'Error creando dataset: {response.status_code} - {response.text}')

if __name__ == "__main__":
    # Valores por defecto
    conf_file = './fusekiDataset.ttl'
    rdf_file = './rdf/rdfGraph.ttl'
    i = 1
    while i < len(sys.argv):
        if sys.argv[i] == '-conf':
            conf_file = sys.argv[i + 1]
            i = i + 1
        elif sys.argv[i] == '-rdf':
            rdf_file = sys.argv[i + 1]
            i = i + 1
        i = i + 1

    fusekiConfiguration("datasetFuseki", conf_file, rdf_file)
