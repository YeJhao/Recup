"""
search.py
Author: Jorge Pagan Saiz and Jiahao Ye
Last update: 2025-10-14

Usage: python search.py -index <indexPath> -infoNeeds <queryFile> -output <resultFile>
"""

import sys
import xml.etree.ElementTree as ET

from intersect import intersect
from whoosh.qparser import QueryParser, MultifieldParser
from whoosh.qparser import OrGroup
from whoosh.query import NumericRange
from whoosh.query import And, Or
from whoosh import scoring
import whoosh.index as index
import spacy

class MySearcher:
    def __init__(self, index_folder, model_type = 'bm25'):
        ix = index.open_dir(index_folder)
        if model_type == 'tfidf':
            self.searcher = ix.searcher(weighting=scoring.TF_IDF())
        else:
            self.searcher = ix.searcher(weighting=scoring.BM25F())

        self.parser = MultifieldParser(["path", "autor", "director", "departamento", "titulo", "descripcion", "subject", "anyo"], 
        schema=ix.schema, 
        group = OrGroup
        )

        try:
            nlp = spacy.load("es_core_news_sm")
        except OSError:
            print("Modelo spaCy 'es_core_news_sm' no encontrado")
        
    def preprocess(self, query_text):
        doc = nlp(query_text)
        # Esrtuctura para guardar cada tipo de entidad que distingue spacy
        entities = {"PERSON": [], "ORG": [], "LOC": [], "GPE": [], "DATE": []}
        for entity in doc.ents:
            if entity.label_ in entities:
                entities[entity.label_].append(entity.text)

        # Subconsultas basadas en el tipo de entidad
        subqueries = []
        for p in entities["PERSON"]:
            subqueries.append(f"autor:{p} OR director:{p}")
        for o in entities["ORG"]:
            subqueries.append(f"departamento:{o}")
        for l in entities["LOC"] + entities["GPE"]:
            subqueries.append(f"descripcion:{l} OR subject:{l}")
        for d in entities["DATE"]:
            subqueries.append(f"anyo:{d}")

        # Combinación de las subconsultas
        final_query_text = f"({query_text})" 
        for q in subqueries:
            final_query_text = final_query_text + f" OR ({q})"

        return final_query_text

    def search(self, query_text, output_file, limit=100):
        query_text = self.preprocess(query_text)
        query = self.parser.parse(query_text)
        results = self.searcher.search(query, limit=limit)

        aux = []
        for result in results:
            aux.append((result["path"], result.score))
        return aux


if __name__ == '__main__':
    index_folder = '../whoosindex'
    info_PATH = None
    output_PATH = '../equipo111.txt'
    i = 1
    while (i < len(sys.argv)):
        if sys.argv[i] == '-index':
            index_folder = sys.argv[i+1]
            i = i + 1
        if(sys.argv[i] == '-infoNeeds'):
            info_PATH = sys.argv[i+1]
            i = i + 1
        if(sys.argv[i] == '-output'):
            output_PATH = sys.argv[i+1]
            i = i + 1
        i = i + 1

    searcher = MySearcher(index_folder)

    if info_PATH:
        tree = ET.parse(info_PATH)
        root = tree.getroot()
        with open(info_PATH, 'r', encoding='utf-8') as f, open(output_PATH, 'w', encoding='utf-8') as out:
            for need in root.findall('informationNeed'):
                identifier = need.find('identifier').text.strip()
                text = need.find('text').text.strip()

                results = searcher.search(text, output_file=output_PATH)
                for doc_id, _ in results:
                    out.write(f"{identifier}\t{doc_id}\n")
    else:
        query = input('Introduce a query (\'q\' for exit): ')
        while query != 'q':
            searcher.search(query, output_file=output_PATH)
            query = input('Introduce a query (\'q\' for exit): ')