"""
carga_xml.py
Author: Jorge Pagan Saiz and Jiahao Ye
Last update: 2025-10-27

Usage: python cargar_xml.py -dir <xmlDir> -output <pandasOutput>
"""

import os
import sys
import pandas as pd
from tqdm import tqdm

class XMLLoader:
    def __init__(self):
        # Definimos las categorías y sus palabras clave asociadas
        self.categorias = {
            'Ciencia': ['fisica', 'quimica', 'biologia', 'ciencia', 'investigacion', 'laboratorio'],
            'Ingenieria': ['informatica', 'electronica', 'mecanica', 'ingenieria', 'tecnologia', 'robotica', 'compilacion'],
            'Matematicas': ['algebra', 'geometria', 'calculo', 'matematicas', 'estadistica', 'probabilidad'], 
            'Artes': ['musica', 'pintura', 'escultura', 'arte', 'dibujo', 'teatro'], 
            'Humanidades' : ['historia', 'filosofia', 'literatura', 'cultura', 'idiomas'], 
            'Salud' : ['medicina', 'enfermeria', 'salud', 'hospital', 'clinica', 'fisioterapia'],
        }
    
    def load_xmls(self,xml_folder):
        all_data = []
        if (os.path.exists(xml_folder)):
            for file in tqdm(sorted(os.listdir(xml_folder))):
                if file.endswith('.xml'):
                    data = self.load_single_xml(xml_folder, file)
                    all_data.append(data)
        return pd.concat(all_data, ignore_index=True)

    def load_single_xml(self, foldername, filename):
        file_path = os.path.join(foldername, filename)
        namespaces = { 
            'oai_dc': 'http://www.openarchives.org/OAI/2.0/oai_dc/',
            'dc': 'http://purl.org/dc/elements/1.1/'
        }
        xpath = '/oai_dc:dc'
        #print(f'Loading XML file: {file_path}') #Debug
        df = pd.read_xml(file_path, xpath=xpath, namespaces=namespaces)
        
        # Normaliza los nombres de columnas (quita 'dc:')
        df.columns = [col.split(":")[-1] for col in df.columns]
        
        return df

    def asignar_categoria(self, row):
        """Asigna una categoría a partir de los metadatos."""
        # Combinar varios campos de texto donde puede aparecer las palabras clave
        text = ""
        for col in ["subject", "relation", "publisher", "type"]:
            if col in row and pd.notna(row[col]):
                text += str(row[col]).lower() + " "
        
        # Buscar en el diccionario de categorías
        for categoria, keywords in self.categorias.items():
            for palabra in keywords:
                if palabra in text:
                    return categoria
        
        # Si no coincide con ninguna categoría
        return "Otros"

if __name__ == '__main__':
    # Valores por defecto
    xml_folder = '../recordsdc'
    output_file = './xml_data.csv'
    i = 1
    while i < len(sys.argv):
        if sys.argv[i] == '-dir':
            xml_folder = sys.argv[i + 1]
            i = i + 1
        elif sys.argv[i] == '-output':
            output_file = sys.argv[i + 1]
            i = i + 1
        i = i + 1

    xml_loader = XMLLoader()
    data_df = xml_loader.load_xmls(xml_folder)

    # Asegurar que existen las columnas necesarias
    for col in ["title", "description", "subject", "relation", "publisher", "type"]:
        if col not in data_df.columns:
            data_df[col] = ""
    
    data_df["categoria"] = data_df.apply(xml_loader.asignar_categoria, axis=1)
    
    data_df = data_df[data_df['categoria'] != "Otros"]

    columnas_resultado = ["title", "description", "categoria"]

    data_df[columnas_resultado].to_csv(output_file, index=False)