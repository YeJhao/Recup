"""
search.py
Author: Jorge Pagan Saiz and Jiahao Ye
Last update: 2025-09-28

Usage: python search.py -index <indexPath> -infoNeeds <queryFile> -output <resultFile>
"""

import sys

from whoosh.qparser import QueryParser, MultifieldParser
from whoosh.qparser import OrGroup
from whoosh import scoring
import whoosh.index as index

class MySearcher:
    def __init__(self, index_folder, model_type = 'tfidf'):
        ix = index.open_dir(index_folder)
        if model_type == 'tfidf':
            self.searcher = ix.searcher(weighting=scoring.TF_IDF())
        else:
            self.searcher = ix.searcher()
        self.parser = MultifieldParser(["autor", "director", "departamento", "titulo", "descripcion", "subject", "anyo"],
                                       ix.schema, group = OrGroup)

    def search(self, query_text, output_file, query_num, limit=100):
        query = self.parser.parse(query_text)
        results = self.searcher.search(query, limit=limit)
        for result in results:
            with open(output_file, 'a', encoding='utf-8') as output:
                doc_id = result.get("path")
                if(doc_id):
                    output.write(f"{query_num}\t{doc_id}\n")
                else:
                    print("Error: Document without dc_identifier field")


if __name__ == '__main__':
    index_folder = '../index'
    info_PATH = None
    output_PATH = '../result.txt'
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
        with open(info_PATH, 'r', encoding='utf-8') as f, open(output_PATH, 'w', encoding='utf-8') as out:
            query_num = 1
            for line in f:
                query = line.strip()
                if(query):
                    searcher.search(query, output_file=output_PATH, query_num=query_num)
                    query_num += 1

    else:
        query = input('Introduce a query (\'q\' for exit): ')
        while query != 'q':
            searcher.search(query, output_file=output_PATH, query_num=1)
            query = input('Introduce a query (\'q\' for exit): ')