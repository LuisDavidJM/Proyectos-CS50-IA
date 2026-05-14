import cv2
import numpy as np
import os
import sys
import tensorflow as tf

from sklearn.model_selection import train_test_split

EPOCHS = 10
IMG_WIDTH = 30
IMG_HEIGHT = 30
NUM_CATEGORIES = 43
TEST_SIZE = 0.4


def main():

    # Check command-line arguments
    if len(sys.argv) not in [2, 3]:
        sys.exit("Usage: python traffic.py data_directory [model.h5]")

    # Get image arrays and labels for all image files
    images, labels = load_data(sys.argv[1])

    # Split data into training and testing sets
    labels = tf.keras.utils.to_categorical(labels)
    x_train, x_test, y_train, y_test = train_test_split(
        np.array(images), np.array(labels), test_size=TEST_SIZE
    )

    # Get a compiled neural network
    model = get_model()

    # Fit model on training data
    model.fit(x_train, y_train, epochs=EPOCHS)

    # Evaluate neural network performance
    model.evaluate(x_test,  y_test, verbose=2)

    # Save model to file
    if len(sys.argv) == 3:
        filename = sys.argv[2]
        model.save(filename)
        print(f"Model saved to {filename}.")


def load_data(data_dir):
    """
    Load image data from directory `data_dir`.

    Assume `data_dir` has one directory named after each category, numbered
    0 through NUM_CATEGORIES - 1. Inside each category directory will be some
    number of image files.

    Return tuple `(images, labels)`. `images` should be a list of all
    of the images in the data directory, where each image is formatted as a
    numpy ndarray with dimensions IMG_WIDTH x IMG_HEIGHT x 3. `labels` should
    be a list of integer labels, representing the categories for each of the
    corresponding `images`.
    """
    images = []
    labels = []

    # Itera a través de cada categoría (0 a 42)
    for category in range(NUM_CATEGORIES):
        print(f"Cargando imágenes de la categoría {category} de 42...")
        # Construyte la ruta de manera independiente del Sistema Operativo
        folder_path = os.path.join(data_dir, str(category))
        
        # Verifica que el directorio exista
        if os.path.isdir(folder_path):
            # Lee cada archivo de imagen dentro de la carpeta de la categoría
            for filename in os.listdir(folder_path):
                img_path = os.path.join(folder_path, filename)
                
                # Lee la imagen como un arreglo multidimensional usando OpenCV
                img = cv2.imread(img_path)
                
                if img is not None:
                    # Redimensiona la imagen a los valores requeridos (30x30)
                    img = cv2.resize(img, (IMG_WIDTH, IMG_HEIGHT))
                    
                    images.append(img)
                    labels.append(category)

    return (images, labels)


def get_model():
    """
    Returns a compiled convolutional neural network model. Assume that the
    `input_shape` of the first layer is `(IMG_WIDTH, IMG_HEIGHT, 3)`.
    The output layer should have `NUM_CATEGORIES` units, one for each category.
    """
    # Construye el modelo secuencial
    model = tf.keras.models.Sequential([
        
        # 1. Primera capa convolucional
        # Aprende 32 filtros diferentes utilizando un kernel de 3x3
        tf.keras.layers.Conv2D(
            32, (3, 3), activation="relu", input_shape=(IMG_WIDTH, IMG_HEIGHT, 3)
        ),
        # Max-pooling para reducir el mapa de características a la mitad y abstraer datos
        tf.keras.layers.MaxPooling2D(pool_size=(2, 2)),

        # 2. Segunda capa convolucional
        # Aprende 64 filtros, ayuda a la red a detectar formas más complejas
        tf.keras.layers.Conv2D(64, (3, 3), activation="relu"),
        tf.keras.layers.MaxPooling2D(pool_size=(2, 2)),

        # 3. Aplanar (Flatten) las unidades
        # Convierte la matriz multidimensional en un vector de una sola dimensión
        tf.keras.layers.Flatten(),

        # 4. Capa Densa (Red neuronal profunda tradicional)
        tf.keras.layers.Dense(128, activation="relu"),
        
        # Dropout: Apaga el 50% de las neuronas aleatoriamente en cada paso.
        # Esto evita el "Overfitting" (sobreajuste), obligando a toda la red a aprender y no depender de unas pocas neuronas.
        tf.keras.layers.Dropout(0.5),

        # 5. Capa de Salida
        # Debe tener 43 neuronas (NUM_CATEGORIES) con función Softmax para convertir la salida en un porcentaje de probabilidad.
        tf.keras.layers.Dense(NUM_CATEGORIES, activation="softmax")
    ])

    # Compila el modelo
    model.compile(
        optimizer="adam",
        loss="categorical_crossentropy",
        metrics=["accuracy"]
    )

    return model


if __name__ == "__main__":
    main()
