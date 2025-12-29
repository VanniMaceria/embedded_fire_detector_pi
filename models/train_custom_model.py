import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Input
from tensorflow.keras.models import Model
import os
import numpy as np

# --- CONFIGURAZIONE ---
DATASET_DIR = "dataset"  # Deve contenere sottocartelle 'fire' e 'no_fire'
OUTPUT_MODEL = "models/fire_model.tflite"
IMG_SIZE = (224, 224)  # Standard MobileNetV2
BATCH_SIZE = 32
EPOCHS = 10


def train():
    if not os.path.exists(DATASET_DIR):
        print(f"ERRORE: Manca la cartella '{DATASET_DIR}'.")
        return

    print("--- 1. Preparazione Dati ---")

    # Data Augmentation per evitare overfitting
    datagen = ImageDataGenerator(
        rescale=1. / 255,  # Normalizza pixel tra 0 e 1
        rotation_range=20,
        width_shift_range=0.2,
        height_shift_range=0.2,
        horizontal_flip=True,
        fill_mode='nearest',
        validation_split=0.2  # Usa il 20% per test
    )

    TARGET_CLASSES = ['no_fire', 'fire']

    print("Caricamento Training Set...")
    train_generator = datagen.flow_from_directory(
        DATASET_DIR,
        target_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        class_mode='binary',
        subset='training',
        shuffle=True,
        classes=TARGET_CLASSES
    )

    print("Caricamento Validation Set...")
    val_generator = datagen.flow_from_directory(
        DATASET_DIR,
        target_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        class_mode='binary',
        subset='validation',
        classes=TARGET_CLASSES
    )

    print(f"MAPPATURA CLASSI: {train_generator.class_indices}")
    # Deve stampare: {'no_fire': 0, 'fire': 1}

    try:
        from sklearn.utils import class_weight
        class_weights = class_weight.compute_class_weight(
            class_weight='balanced',
            classes=np.unique(train_generator.classes),
            y=train_generator.classes
        )
        weights_dict = dict(enumerate(class_weights))
        print(f"Pesi calcolati automaticamente: {weights_dict}")
    except:
        print("sklearn non installato. Uso pesi manuali.")
        weights_dict = {0: 5.0, 1: 1.0}

    print("--- 2. Costruzione Modello (MobileNetV2) ---")
    base_model = MobileNetV2(weights='imagenet', include_top=False, input_tensor=Input(shape=(224, 224, 3)))
    base_model.trainable = False  # Congeliamo i pesi base

    x = base_model.output
    x = GlobalAveragePooling2D()(x)
    x = Dense(128, activation='relu')(x)

    # Output Sigmoide: Restituisce la probabilità che sia Classe 1 (cioè FIRE)
    predictions = Dense(1, activation='sigmoid')(x)

    model = Model(inputs=base_model.input, outputs=predictions)
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

    print("--- 3. Addestramento ---")
    model.fit(
        train_generator,
        epochs=EPOCHS,
        validation_data=val_generator,
        class_weight=weights_dict
    )

    print("--- 4. Conversione a TFLite ---")
    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    tflite_model = converter.convert()

    if not os.path.exists("models"): os.makedirs("models")
    with open(OUTPUT_MODEL, "wb") as f:
        f.write(tflite_model)

    print(f"✅ MODELLO CREATO: {OUTPUT_MODEL}")
    print("Logica: 0.0 = Sicuro, 1.0 = Incendio")


if __name__ == "__main__":
    train()