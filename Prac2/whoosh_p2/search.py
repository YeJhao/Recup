"""
search.py
Author: Jorge Pagan Saiz and Jiahao Ye
Last update: 2025-09-28

Usage: python search.py -index <indexPath> -infoNeeds <queryFile> -output <resultFile>
"""

import sys

from intersect import intersect
from whoosh.qparser import QueryParser, MultifieldParser
from whoosh.qparser import OrGroup
from whoosh.query import NumericRange
from whoosh.query import And, Or
from whoosh import scoring
import whoosh.index as index

class MySearcher:
    def __init__(self, index_folder, model_type = 'tfidf'):
        ix = index.open_dir(index_folder)
        if model_type == 'tfidf':
            self.searcher = ix.searcher(weighting=scoring.TF_IDF())
        else:
            self.searcher = ix.searcher()
        self.parser = MultifieldParser(["autor", "director", "departamento", "titulo", "descripcion", "subject", "anyo", "east", "north", "west", "south"], schema=
                                       ix.schema, group = OrGroup)

    def search(self, query_text, output_file, query_num, limit=100):
        if query_text.strip().lower().startswith("spatial"):
            res = []
            res_score = []
            query = query_text.strip().split(" ")
            spatial_query = query[0]
            text_query = query[1] if len(query) > 1 else ""
            print("", text_query)

            query = spatial_query.strip()[8:].strip().split(",")
            west = float(query[0])
            east = float(query[1])
            south = float(query[2])
            north = float(query[3])
            westRangeQuery = NumericRange("west", start = None, end = east)
            eastRangeQuery = NumericRange("east", start = west, end = None)
            southRangeQuery = NumericRange("south", start = None, end = north)
            northRangeQuery = NumericRange("north", start = south, end = None)

            spatialQuery = And([westRangeQuery, eastRangeQuery, southRangeQuery, northRangeQuery])
            final_query = Or([spatialQuery, self.parser.parse(text_query)]) if text_query else spatialQuery
            results = self.searcher.search(final_query, limit=limit)

            for result in results:
                doc_id = result.get("path")
                doc_west = result.get("west")
                doc_east = result.get("east")
                doc_south = result.get("south")
                doc_north = result.get("north")
                if(doc_west is not None and doc_east is not None and doc_south is not None and doc_north is not None) and intersect(west, east, south, north, doc_west, doc_east, doc_south, doc_north):
                        if(doc_id):
                            print("Debug: Found document", doc_id)
                            res.append(doc_id)
                            res_score.append(result.score)
                        else:
                            print("Error: Document without dc_identifier field")
                else:
                    if doc_id:
                        print("Debug: Found document without spatial data", doc_id)
                        res.append(doc_id)
                        res_score.append(result.score)
            
            # Extraer solo el número al inicio de cada línea
            numbers = [line.split("-")[0] for line in res]

            scores_str = [f"{s:.2f}" for s in res_score]

            # Unirlos por comas
            result = ",".join(numbers)
            result_scores = ",".join(scores_str)

            with open(output_file, 'a', encoding='utf-8') as output:
                output.write(f"{query_num}\t{len(numbers)}\t{result}\t{result_scores}\n")
            
        else:
            query = self.parser.parse(query_text)
            results = self.searcher.search(query, limit=limit)
            for result in results:
                with open(output_file, 'a', encoding='utf-8') as output:
                    doc_id = result.get("path")
                    if(doc_id):
                        output.write(f"{doc_id}\n")
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