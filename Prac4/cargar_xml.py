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
from sklearn.model_selection import train_test_split

class XMLLoader:
    def __init__(self):
        # Definimos las categorías y sus palabras clave asociadas
        self.categorias = {
            'Ciencias': ['Fisica', 'Quimica', 'Biologia', 'Matemáticas', 'Geologia']
            'Ingenieria': ['Informatica', 'Eléctrica' 'Electronica', 'Mecanica', 'Telecomunicaciones'], 'Industrial',
            'Ciencias de la salud': ['Medicina', 'Enfermeria', 'Fisioterapia', 'Psicologia', 'Veterinaria'], 
            'Artes y Humanidades': ['Bellas Artes', 'Filosofia', 'Historia', 'Lenguas Modernas'],
            'Sociales' : ['Deporte', 'Derecho', 'Economia', 'ADE', 'Empresa'] 
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
    output_dir = './xml_data'
    i = 1
    while i < len(sys.argv):
        if sys.argv[i] == '-dir':
            xml_folder = sys.argv[i + 1]
            i = i + 1
        elif sys.argv[i] == '-output':
            output_dir = sys.argv[i + 1]
            i = i + 1
        i = i + 1
    
    os.makedirs(output_dir, exist_ok=True)

    xml_loader = XMLLoader()
    data_df = xml_loader.load_xmls(xml_folder)

    # Asegurar que existen las columnas necesarias
    for col in ["title", "description", "subject", "relation", "publisher", "type"]:
        if col not in data_df.columns:
            data_df[col] = ""
    
    data_df["category"] = data_df.apply(xml_loader.asignar_categoria, axis=1)
    
    data_df = data_df[data_df['category'].notna()]

    # Dividir en entrenamiento y test
    train_df, test_df = train_test_split(data_df, test_size=0.2, random_state=42, stratify=data_df["category"])

    columnas_resultado = ["title", "description", "category"]

    train_df[columnas_resultado].to_csv(os.path.join(output_dir, "zaguan_train.csv"), index=False)
    test_df[columnas_resultado].to_csv(os.path.join(output_dir, "zaguan_test.csv"), index=False)