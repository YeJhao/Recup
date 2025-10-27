"""
clasificadorTexto.py
Author: Jorge Pagan Saiz and Jiahao Ye
Last update: 2025-10-27

Usage: python clasificadorTexto.py -dir <zaguanDir> -output <resultsDir>
"""

import os
import sys
import pandas as pd
import commonFunctions 
from commonFunctions import set_random_seed, Sequential, Adam, Dense, Embedding, LSTM

class MyClassifier:
    def __init__(self, pandas):
        self.data = pandas
        self.categorias = {
            'Ciencia': ['fisica', 'quimica', 'biologia', 'ciencia', 'investigacion', 'laboratorio'],
            'Ingenieria': ['informatica', 'electronica', 'mecanica', 'ingenieria', 'tecnologia', 'robotica', 'compilacion'],
            'Matematicas': ['algebra', 'geometria', 'calculo', 'matematicas', 'estadistica', 'probabilidad'], 
            'Artes': ['musica', 'pintura', 'escultura', 'arte', 'dibujo', 'teatro'], 
            'Humanidades' : ['historia', 'filosofia', 'literatura', 'cultura', 'idiomas'], 
            'Salud' : ['medicina', 'enfermeria', 'salud', 'hospital', 'clinica', 'fisioterapia'],
        }
        self.resultados = {}

    def gen_Categories(self):
        # Por cada dato
        for _, row in self.data.iterrows():
            title = str(row['title']).toLowerCase()
            description = str(row['description']).toLowerCase()
            # Por cada categoría
            asignado = False
            for categoria, claves in self.categorias.items() and not asignado:
                # Por cada palabra clave
                for clave in claves and not asignado:
                    # Si la palabra clave está en el título o la descripción
                    if clave in title.lower() or clave in description.lower():
                        identificador = row['identifier']
                        self.resultados[identificador] = categoria
                        asignado = True
                        break
            if not asignado:
                identificador = row['identifier']
                self.resultados[identificador] = 'nula'

        return self.resultados

    def createModelLSTM(vocSize):
        # Usar get_vocabulary del TextVectorization para obtener el tamaño del vocabulario
        EMBEDDINGS_SIZE = 50 # Número de dimensiones del vector de Embeddings.
        model = Sequential()
        model.add(Embedding(vocSize, EMBEDDINGS_SIZE, mask_zero=True)) # mask_zero hace que se cree una máscara indicando que posiciones son padding, esto evita que aprenda patrones de las casillas vacías.
        model.add(LSTM(32))
        model.add(Dense(12, activation = 'relu'))
        model.add(Dense(4, activation = 'softmax'))
        model.compile(loss = 'CategoricalCrossentropy', optimizer = Adam(1e-4), metrics = ['accuracy']) # type: ignore
        return model

    def evaluateModel():
        pass

if __name__ == '__main__':
    # Valores por defecto
    dir_folder = '../recordsdc'
    output_folder = '../results/clasificadorTexto'
    set_random_seed(0)  # Fijamos la semilla para reproducibilidad.
    i = 1
    while i < len(sys.argv):
        if sys.argv[i] == '-dir':
            dir_folder = sys.argv[i + 1]
            i = i + 1
        elif sys.argv[i] == '-output':
            output_folder = sys.argv[i + 1]
            i = i + 1
        i = i + 1

    my_classifier = MyClassifier()