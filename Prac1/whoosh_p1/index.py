"""
index.py
Author: Jorge Pagan Saiz and Jiahao Ye
Last update: 2025-09-27

Simple program to create an inverted index with the contents of text/xml files contained in a docs folder
This program is based on the whoosh library. See https://pypi.org/project/Whoosh/ .
Usage: python index.py -docs <docsPath> -index <indexPath>
"""

from whoosh.index import create_in
from whoosh.fields import *
from whoosh.analysis import LanguageAnalyzer
from datetime import datetime

import os

import xml.etree.ElementTree as ET

def create_folder(folder_name):
    if (not os.path.exists(folder_name)):
        os.mkdir(folder_name)

class MyIndex:
    def __init__(self,index_folder):
        # TODO: create new LanguageAnalyzer using Whoosh libraries
        language_analyzer = LanguageAnalyzer(lang="es" , expression=r"\w+")
        schema = Schema(path=ID(stored=True), autor=TEXT(analyzer=language_analyzer),
                        director=TEXT(analyzer=language_analyzer), departamento=TEXT(analyzer=language_analyzer),
                        titulo=TEXT(analyzer=language_analyzer), descripcion=TEXT(analyzer=language_analyzer),
                        subject=TEXT(analyzer=language_analyzer), anyo=NUMERIC())
        create_folder(index_folder)
        index = create_in(index_folder, schema)
        self.writer = index.writer()

    def index_docs(self,docs_folder):
        if (os.path.exists(docs_folder)):
            for file in sorted(os.listdir(docs_folder)):
                # print(file)
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
        
        namespaces = { 'dc': 'http://purl.org/dc/elements/1.1/' }

        directores = ""
        subjects = ""

        path_element = root.find('.//dc:identifier', namespaces)
        autor_element = root.find('.//dc:autor', namespaces)
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

        #raw_text = "".join(root.itertext())
        # break into lines and remove leading and trailing space on each
        #text = ' '.join(line.strip() for line in raw_text.splitlines() if line)
        # print(text)
        
        self.writer.add_document(path=path_element.text, autor=autor_element.text, director=str(directores),
                                 departamento=departamento_element.text, titulo=title_element.text,
                                 descripcion=description_element.text, subject=str(subjects),
                                 anyo=anyo_element.text)

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


