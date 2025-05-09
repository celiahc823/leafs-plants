# -*- coding: utf-8 -*-
"""Leafs plants.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/16zG-TQ6NMggmNyrdXF9glWr2RArEOC-F

#Enfermedades de plantas

https://www.tensorflow.org/datasets/catalog/plant_leaves?hl=es-419
"""

#  IMPORTAR LIBRERÍAS

import tensorflow as tf
import tensorflow_datasets as tfds
import numpy as np
import matplotlib.pyplot as plt
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras import layers, models
from tensorflow.keras.optimizers import Adam
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay

import tensorflow_datasets as tfds

# PARÁMETROS

IMG_SIZE = 224
BATCH_SIZE = 32
EPOCHS = 10

# CARGA Y PREPROCESAMIENTO DEL DATASET

def preprocess(example):
    image = example['image']
    label = example['label']
    image = tf.image.resize(image, (IMG_SIZE, IMG_SIZE))
    image = tf.cast(image, tf.float32) / 255.0
    return image, label

print("Cargando dataset...")
dataset, info = tfds.load('plant_leaves', split='train', with_info=True)
dataset = dataset.map(preprocess)

print("Dividiendo dataset en entrenamiento y validación...")

images = []
labels = []

# Asegurar forma consistente y normalización
for image, label in dataset.as_numpy_iterator():
    images.append(image)
    labels.append(label)

images = np.array(images)
labels = np.array(labels)

# Dividir 80/20
total_size = len(images)
train_size = int(0.8 * total_size)

train_images = images[:train_size]
train_labels = labels[:train_size]
val_images = images[train_size:]
val_labels = labels[train_size:]

# Crear datasets de entrenamiento y validación
train_ds = tf.data.Dataset.from_tensor_slices((train_images, train_labels)).batch(BATCH_SIZE).prefetch(tf.data.AUTOTUNE)
val_ds = tf.data.Dataset.from_tensor_slices((val_images, val_labels)).batch(BATCH_SIZE).prefetch(tf.data.AUTOTUNE)

# CONSTRUIR MODELO CON TRANSFERENCIA DE APRENDIZAJE

print("Construyendo modelo con MobileNetV2...")
base_model = MobileNetV2(weights='imagenet', include_top=False, input_shape=(224, 224, 3))
base_model.trainable = True

for layer in base_model.layers[:-10]:
    layer.trainable = False

model = models.Sequential([
    base_model,
    layers.GlobalAveragePooling2D(),
    layers.Dense(128, activation='relu'),
    layers.Dropout(0.5),
    layers.Dense(22, activation='softmax')  # 22 clases
])

# COMPILAR Y ENTRENAR

print("Entrenando modelo...")
model.compile(optimizer=Adam(1e-4), loss='sparse_categorical_crossentropy', metrics=['accuracy'])

history = model.fit(train_ds, validation_data=val_ds, epochs=EPOCHS)

print("Accuracy final de entrenamiento:", history.history['accuracy'][-1])
print("Accuracy final de validación:", history.history['val_accuracy'][-1])

plt.plot(history.history['accuracy'])
plt.plot(history.history['val_accuracy'])
plt.title('Accuracy')
plt.legend(['train', 'val'])
plt.show()

# Asegurar la carpeta de resultados
os.makedirs("results", exist_ok=True)

# Curva de Pérdida (Loss)
plt.figure(figsize=(10, 5))
plt.plot(history.history['loss'], label='Entrenamiento')
plt.plot(history.history['val_loss'], label='Validación')
plt.title('Pérdida por Época')
plt.xlabel('Épocas')
plt.ylabel('Pérdida')
plt.legend()
plt.grid(True)
plt.savefig('results/loss_curve.png')
plt.show()

#  MATRIZ DE CONFUSIÓN
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay

print("Calculando matriz de confusión...")

# Asegurar que val_images están en formato tensor
X_val = tf.convert_to_tensor(val_images)
y_true = val_labels

# Obtener predicciones
y_pred = model.predict(X_val)
y_pred_classes = np.argmax(y_pred, axis=1)

# Matriz de confusión
cm = confusion_matrix(y_true, y_pred_classes)
disp = ConfusionMatrixDisplay(confusion_matrix=cm)
disp.plot(cmap='viridis')
plt.title("Matriz de Confusión")
plt.show()

#  Clases utilziadas para la validación
print("\n Clases presentes en el conjunto de validación:")
val_labels_array = np.array(val_labels)
clases_validadas = np.unique(val_labels_array)
label_names = info.features['label'].names

for i in clases_validadas:
    print(f"{i}: {label_names[i]}")

import os
os.makedirs("results", exist_ok=True)

plt.savefig('results/accuracy_curve.png')
plt.savefig('results/accuracy_loss_curve.png')
plt.savefig('results/confusion_matrix.png')