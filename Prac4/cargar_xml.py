"""
carga_xml.py
Author: Jorge Pagan Saiz and Jiahao Ye
Last update: 2025-10-27

Usage: python cargar_xml.py -dir <xmlDir> -output <pandasOutput>
"""

import os
import sys
import pandas as pd

class XMLLoader:
    def load_xmls(self,xml_folder):
        all_data = []
        if (os.path.exists(xml_folder)):
            for file in sorted(os.listdir(xml_folder)):
                if file.endswith('.xml'):
                    data = self.load_single_xml(xml_folder, file)
                    all_data.append(data)
        return pd.concat(all_data, ignore_index=True)

    def load_single_xml(self, foldername, filename):
        voc_size = 0
        file_path = os.path.join(foldername, filename)
        namespaces = { 
            'oai_dc': 'http://www.openarchives.org/OAI/2.0/oai_dc/',
            'dc': 'http://purl.org/dc/elements/1.1/'
        }
        xpath = '/oai_dc:dc'
        print(f'Loading XML file: {file_path}') #Debug
        df = pd.read_xml(file_path, xpath=xpath, namespaces=namespaces)
        
        return df

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
    data_df.to_csv(output_file, index=False)