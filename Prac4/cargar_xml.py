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
            'Artes y Humanidades' : ['Bellas Artes', 'Estudios Clásicos', 'Estudios Ingleses', 'Filología Hispánica', 'Filosofía', 'Historia', 'Historia del Arte', 'Lenguas Modernas'],
            'Ciencias' : ['Biotecnología', 'Ciencia y Tecnología de los Alimentos', 'Ciencias Ambientales', 'Física', 'Geología', 'Matemáticas', 'Óptica y Optometría', 'Química'],
            'Ciencias de la Salud' : ['Enfermería', 'Fisioterapia','Medicina', 'Nutrición Humana y Dietética', 'Odontología', 'Psicología', 'Terapia Ocupacional', 'Veterinaria'],
            'Ciencias Sociales y Jurídicas' : ['ADE', 'Administración y Dirección de Empresas', 'Ciencias de la Actividad Física y del Deporte', 'Derecho', 'Economía', 'Finanzas y Contabilidad', 'Geografía y Ordenación del Territorio', 'Geografía', 'Gestión y Administración Pública', 'Magisterio', 'Marketing', 'Periodismo', 'Relaciones Laborales y Recursos Humanos', 'Trabajo Social', 'Turismo'],
            'Ingeniería y Arquitectura' : ['Arquitectura', 'Arquitectura Técnica', 'Defensa y Seguridad', 'Ingenieria Agroalimentaria y del Medio Rural', 'Ingeniería Aeroespacial', 'Ingeniería Eléctrica', 'Ingeniería Electrónica y Automática', 'Ingeniería Biomédica', 'Ingeniería Civil', 'Ingeniería de Tecnologías de Telecomunicación', 'Ingeniería Eléctrica', 'Ingeniería Informática', 'Ingeniería Mecánica', 'Ingeniería Mecatrónica', 'Ingeniería Química']
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
        subj = ''
        if 'subject' in row and pd.notna(row['subject']):
            subj = row['subject']

        # Normalizar a texto
        if isinstance(subj, (list, tuple)):
            subj_text = ' '.join([str(s) for s in subj]).lower()
        else:
            subj_text = str(subj).lower()

        if subj_text.strip() == '' or subj_text == 'nan':
            return 'Otros'

        for categoria, keywords in self.categorias.items():
            for palabra in keywords:
                if palabra.lower() in subj_text:
                    return categoria

        return 'Otros'

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