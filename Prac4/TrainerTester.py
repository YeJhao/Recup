#-------------------------------------------------------------------------------
# Entrenamiento y evaluación del clasificador de texto
#-------------------------------------------------------------------------------
import os
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix
from commonFunctions import Chronometer, saveResults

#-------------------------------------------------------------------------------
def trainerTester(model, data, epochs, dir_name, categories):
    dir_path = f'results/{dir_name}'
    os.makedirs(dir_path, exist_ok=True)

    X_train, y_train, X_test, y_test = data

    print('----------------------------------------------------')
    print('Training the model')
    print('----------------------------------------------------')

    with Chronometer() as chronometer:
        history = model.fit(
            X_train, y_train,
            epochs=epochs,
            batch_size=64,
            validation_split=0.2,
            verbose=1
        )

    saveResults(model, history, chronometer.message, dir_path)

    # Evaluación
    scores = model.evaluate(X_test, y_test, verbose=0)
    accuracy = scores[1]

    # Predicciones
    y_pred = np.argmax(model.predict(X_test, verbose=0), axis=1)
    y_true = np.argmax(y_test, axis=1)

    # Matriz de confusión
    cm = confusion_matrix(y_true, y_pred)

    # Guardamos precision.txt
    with open(os.path.join(dir_path, 'precision.txt'), 'w', encoding='utf-8') as f:
        f.write(f"Accuracy: {accuracy:.4f}\n")

    # Guardamos confusion.txt
    with open(os.path.join(dir_path, 'confusion.txt'), 'w', encoding='utf-8') as f:
        f.write('Confusion matrix (rows=true, cols=pred):\n')
        np.savetxt(f, cm, fmt='%d')
        f.write('\nLabels:\n')
        for i, cat in enumerate(categories):
            f.write(f"{i}: {cat}\n")

    # Guardamos gráfica de precisión
    plt.figure(figsize=(8, 5))
    plt.plot(history.history['accuracy'], label='Train')
    plt.plot(history.history['val_accuracy'], label='Validation')
    plt.xlabel('Epochs')
    plt.ylabel('Accuracy')
    plt.title('Evolución de la precisión')
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(dir_path, 'error.jpg'))
    plt.close()

    print(f"[i] Final accuracy: {accuracy:.4f}")
    print(f"[i] Results saved in: {dir_path}")
