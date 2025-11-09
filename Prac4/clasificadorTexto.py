"""
clasificadorTexto.py
Author: Jorge Pagan Saiz and Jiahao Ye
Last update: 2025-10-27

Usage: python clasificadorTexto.py -dir <zaguanDir> -output <resultsDir>
"""

from commonFunctions import set_random_seed, Sequential, Embedding, LSTM, Dense, Adam
from TrainerTester import trainerTester
from DataReader import dataReader

def createModel(vocab_size, num_classes):
    EMBEDDINGS_SIZE = 128
    model = Sequential()
    model.add(Embedding(vocab_size, EMBEDDINGS_SIZE, mask_zero=True))
    model.add(LSTM(64, dropout=0.3, recurrent_dropout=0.3))
    model.add(Dense(64, activation='relu'))
    model.add(Dense(num_classes, activation='softmax'))
    model.compile(loss='categorical_crossentropy',
                  optimizer=Adam(1e-4),
                  metrics=['accuracy'])
    return model

#-------------------------------------------------------------------------------
# Carga de datos, entrenamiento y test del modelo anteriormente definido.
#-------------------------------------------------------------------------------
EPOCHS = 30

if __name__ == '__main__':
    set_random_seed(0)
    data, vocab_size, categories = dataReader(fraction=1)
    model = createModel(vocab_size, len(categories))
    trainerTester(model, data, EPOCHS, 'zaguan_TextClassifier_LSTM', categories)
