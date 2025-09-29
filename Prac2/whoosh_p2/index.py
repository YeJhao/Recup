"""
index.py
Author: Jorge Pagan Saiz and Jiahao Ye
Last update: 2025-09-29

Simple program to create an inverted index with the contents of text/xml files contained in a docs folder
This program is based on the whoosh library. See https://pypi.org/project/Whoosh/ .
Usage: python index.py -docs <docsPath> -index <indexPath>
"""

from whoosh.index import create_in
from whoosh.fields import *
from whoosh.analysis import LanguageAnalyzer
from datetime import datetime

from analyzer import CustomAnalyzer

import os

import xml.etree.ElementTree as ET

def create_folder(folder_name):
    if (not os.path.exists(folder_name)):
        os.mkdir(folder_name)

class MyIndex:
    def __init__(self,index_folder):
        language_analyzer = CustomAnalyzer()
        schema = Schema(path=ID(stored=True), autor=TEXT(analyzer=language_analyzer),
                        director=TEXT(analyzer=language_analyzer), departamento=TEXT(analyzer=language_analyzer),
                        titulo=TEXT(analyzer=language_analyzer), descripcion=TEXT(analyzer=language_analyzer),
                        subject=TEXT(analyzer=language_analyzer), anyo=NUMERIC(), east=NUMERIC(stored=True), north=NUMERIC(stored=True),
                        west=NUMERIC(stored=True), south=NUMERIC(stored=True))
        create_folder(index_folder)
        index = create_in(index_folder, schema)
        self.writer = index.writer()

    def index_docs(self,docs_folder):
        if (os.path.exists(docs_folder)):
            for file in sorted(os.listdir(docs_folder)):
                #print(file) # Debug: print the file name being processed
                if file.endswith('.xml'):
                    self.index_xml_doc(docs_folder, file)
                elif file.endswith('.txt'):
                    self.index_txt_doc(docs_folder, file)
        self.writer.commit()

    # No se utiliza, se podría eliminar
    def index_txt_doc(self, foldername,filename):
        file_path = os.path.join(foldername, filename)
        # print(file_path)
        with open(file_path) as fp:
            text = ' '.join(line for line in fp if line)
            
        # print(text)
        
        atime = datetime.fromtimestamp(os.path.getmtime(file_path))
        self.writer.add_document(path=filename, content=text, stored=atime)

    def index_xml_doc(self, foldername, filename):
        file_path = os.path.join(foldername, filename)
        # print(file_path)
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        namespaces = { 'dc': 'http://purl.org/dc/elements/1.1/', 'ows': 'http://www.opengis.net/ows' }

        directores = ""
        subjects = ""

        path_element = root.find('.//dc:identifier', namespaces)
        autor_element = root.find('.//dc:creator', namespaces)
        director_element = root.findall('.//dc:contributor', namespaces)

        for dir in director_element:
            directores += str(dir.text) + " "

        departamento_element = root.find('.//dc:publisher', namespaces)

        title_element = root.find('.//dc:title', namespaces)
        description_element = root.find('.//dc:description', namespaces)

        subject_element = root.findall('.//dc:subject', namespaces)

        for subj in subject_element:
            subjects += str(subj.text) + " "

        anyo_element = root.find('.//dc:date', namespaces)

        lower_corner_element = root.find('.//ows:LowerCorner', namespaces)
        upper_corner_element = root.find('.//ows:UpperCorner', namespaces)

        lower_lat, upper_lat, lower_lon, upper_lon = None, None, None, None

        # Partimos las coordenadas y pasamos a float
        if lower_corner_element is not None:
            lower_lat, lower_lon = map(float, lower_corner_element.text.strip().split())

        if upper_corner_element is not None:
            upper_lat, upper_lon = map(float, upper_corner_element.text.strip().split())


        #raw_text = "".join(root.itertext())
        # break into lines and remove leading and trailing space on each
        #text = ' '.join(line.strip() for line in raw_text.splitlines() if line)
        # print(text)
        # print(path_element.text, lower_lat, upper_lat, lower_lon, upper_lon)
        
        self.writer.add_document(path=path_element.text,
                                 autor=autor_element.text if autor_element is not None else "",
                                 director=str(directores),
                                 departamento=departamento_element.text if departamento_element is not None else "",
                                 titulo=title_element.text if title_element is not None else "",
                                 descripcion=description_element.text if description_element is not None else "",
                                 subject=str(subjects),
                                 anyo=int(anyo_element.text) if anyo_element is not None else 0,
                                 east=upper_lat, north=upper_lon, west=lower_lat, south=lower_lon)

if __name__ == '__main__':

    index_folder = '../whooshindex'
    docs_folder = '../docs'
    i = 1
    while i < len(sys.argv):
        if sys.argv[i] == '-index':
            index_folder = sys.argv[i + 1]
            i = i + 1
        elif sys.argv[i] == '-docs':
            docs_folder = sys.argv[i + 1]
            i = i + 1
        i = i + 1

    my_index = MyIndex(index_folder)
    my_index.index_docs(docs_folder)


