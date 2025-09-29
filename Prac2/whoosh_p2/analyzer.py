"""
index.py
Author: Jorge Pagan Saiz and Jiahao Ye
Last update: 2025-09-28

Language analyzer para la práctica 1 de Recuperación de Información usando
librerías Whoosh.
"""

from whoosh.analysis import RegexTokenizer, LowercaseFilter, StopFilter, Filter
from nltk.stem.snowball import SnowballStemmer

class SnowballStemFilter(Filter):
    def __init__(self):
        self.stemmer = SnowballStemmer(language="spanish")

    def __call__(self, tokens):
        for t in tokens:
            t.text = self.stemmer.stem(t.text)
            yield t

def CustomAnalyzer():
    return RegexTokenizer() | LowercaseFilter() | StopFilter(lang="es") | SnowballStemFilter()