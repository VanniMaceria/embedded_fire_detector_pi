import os
import numpy as np

# Gestione import (PC vs Raspberry)
try:
    import tflite_runtime.interpreter as tflite
except ImportError:
    try:
        import tensorflow.lite as tflite
    except ImportError:
        raise ImportError("Manca la libreria TFLite.")


class InferenceEngine:
    """
    Motore di inferenza TFLite puro.
    Restituisce direttamente la probabilità di incendio (0.0 - 1.0).
    """

    def __init__(self, model_path: str = None):
        if model_path is None:
            model_path = os.path.join("models", "fire_model.tflite")

        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Modello non trovato: {model_path}")

        print(f"[INFO] Caricamento TFLite: {model_path}")

        self.interpreter = tflite.Interpreter(model_path=model_path)
        self.interpreter.allocate_tensors()

        # Dettagli input/output
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()

        self.input_index = self.input_details[0]['index']
        self.output_index = self.output_details[0]['index']

        # Espone le dimensioni per il FireMonitor
        self.input_shape = self.input_details[0]['shape']
        self.height = self.input_shape[1]
        self.width = self.input_shape[2]

    def predict(self, processed_image: np.ndarray) -> float:
        """
        Input: Immagine RGB 224x224 normalizzata (0-1).
        Output: Probabilità incendio (float).
        """
        img = processed_image.astype(np.float32)

        # Aggiungi dimensione batch (1, H, W, 3)
        if img.ndim == 3:
            img = np.expand_dims(img, axis=0)

        self.interpreter.set_tensor(self.input_index, img)
        self.interpreter.invoke()

        output_data = self.interpreter.get_tensor(self.output_index)

        # Il valore è già P(Classe 1), cioè P(Fire)
        val = float(output_data.flatten()[0])

        return val