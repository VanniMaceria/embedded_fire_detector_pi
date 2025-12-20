import os
from pathlib import Path
from typing import Optional
import numpy as np
try:
    from keras.models import load_model
except ImportError:
    load_model = None


class InferenceEngine:
    """Wrapper per il modello di ML.
    Carica un modello Keras (passando `model_path`) e fornisce `predict()`.
    """

    def __init__(self, model_path: Optional[str] = None):
        if model_path is None:
            model_path = os.path.join("models", "Fire-64x64-color-v7-soft.h5")

        model_file = Path(model_path)

        # Verifica esistenza file
        if not model_file.exists():
            raise FileNotFoundError(f"Modello non trovato: {model_file}")

        # Verifica disponibilità libreria
        if load_model is None:
            raise RuntimeError("Keras/TensorFlow non installato. Impossibile caricare il modello.")

        # Caricamento
        self.model = load_model(str(model_file))

    def predict(self, processed_image: np.ndarray) -> float:
        """Esegue l'inferenza sul frame fornito."""
        if not hasattr(self, "model") or self.model is None:
            raise RuntimeError("Modello non caricato")

        img = np.array(processed_image)

        # Batch dimension
        batch = np.expand_dims(img, axis=0)

        preds = self.model.predict(batch)
        try:
            prob = float(np.asarray(preds).reshape(-1)[0])
        except Exception:
            raise RuntimeError("Output del modello non interpretabile come probabilità")

        # Se modello ritorna percentuale 0..100 -> normalizziamo
        if 1.0 < prob <= 100.0:
            prob = prob / 100.0

        prob = max(0.0, min(1.0, prob))
        return prob