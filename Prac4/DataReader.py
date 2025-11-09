#-------------------------------------------------------------------------------
# Lector y procesador para el clasificador de texto
#-------------------------------------------------------------------------------
import pandas as pd
import numpy as np
from commonFunctions import cleanTexts, to_categorical, TextVectorization

# Lee CSV con columnas: Titulo, Descripción, Categoría
def __readDataframe(file):
    df = pd.read_csv(file, index_col=False)
    df['Text'] = df['title'].astype(str) + '. ' + df['description'].astype(str)
    df.drop(['title', 'description'], axis=1, inplace=True)
    return df

def dataReader(fraction=1, max_seq_length=200):
    train_df = __readDataframe('data/zaguan_train.csv')
    test_df = __readDataframe('data/zaguan_test.csv')

    train_df = train_df.sample(frac=fraction, random_state=0)

    # Limpieza de texto
    X_train = cleanTexts(train_df['Text'].values, mode='classification')
    X_test = cleanTexts(test_df['Text'].values, mode='classification')

    # Codificación de categorías
    categories = sorted(train_df['category'].unique())
    cat_to_idx = {c: i for i, c in enumerate(categories)}
    y_train = to_categorical([cat_to_idx[c] for c in train_df['category'].values])
    y_test = to_categorical([cat_to_idx[c] for c in test_df['category'].values])

    # Vectorización
    vectorizer = TextVectorization(output_mode='int',
                                   output_sequence_length=max_seq_length)
    vectorizer.adapt(X_train)
    X_train = vectorizer(X_train)
    X_test = vectorizer(X_test)

    return (X_train, y_train, X_test, y_test), len(vectorizer.get_vocabulary()), categories
