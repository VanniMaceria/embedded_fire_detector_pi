import os
from pathlib import Path
from typing import Optional

import cv2
import numpy as np

try:
    from tensorflow.keras.models import load_model
except Exception:
    
    load_model = None


class InferenceEngine:
    """Wrapper per il modello di ML.
    Carica un modello Keras (passando `model_path`) e fornisce `predict()`.
    """

    IMG_SIZE = (64, 64)

    def __init__(self, model_path: Optional[str] = None):
        if model_path is None:
            model_path = os.path.join("models", "Fire-64x64-color-v7-soft.h5")

        model_file = Path(model_path)
        if not model_file.exists():
            if load_model is None:
                raise RuntimeError("TensorFlow/Keras non disponibile e modello mancante")

        if load_model is None:
            if not hasattr(self, "model"):
                mod = __import__(__name__)
                if hasattr(mod, "load_model") and callable(getattr(mod, "load_model")):
                    self.model = getattr(mod, "load_model")(str(model_file))
                else:
                    raise RuntimeError("load_model non disponibile; installa tensorflow o mockalo nei test")
        else:
            self.model = load_model(str(model_file))

    def predict(self, processed_image: np.ndarray) -> float:
        """Esegue l'inferenza sul frame fornito.

        Preprocessing minimo (resize a 64x64 e normalizzazione) e chiamata a
        `self.model.predict`. Restituisce un float in [0,1].
        """
        if not hasattr(self, "model") or self.model is None:
            raise RuntimeError("Modello non caricato")

        img = np.array(processed_image)

        # Gestione immagini grayscale
        if img.ndim == 2:
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        if img.ndim == 3 and img.shape[2] == 1:
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

        # Resize a IMG_SIZE
        target = (self.IMG_SIZE[1], self.IMG_SIZE[0])
        if (img.shape[0], img.shape[1]) != (self.IMG_SIZE[0], self.IMG_SIZE[1]):
            img = cv2.resize(img, target, interpolation=cv2.INTER_AREA)

        # Normalizza in [0,1]
        if not np.issubdtype(img.dtype, np.floating):
            img = img.astype('float32') / 255.0
        else:
            img = img.astype('float32')
            if img.max() > 1.0:
                img = img / 255.0

        # Batch dimension
        batch = np.expand_dims(img, axis=0)

        preds = self.model.predict(batch)
        try:
            prob = float(np.asarray(preds).reshape(-1)[0])
        except Exception:
            raise RuntimeError("Output del modello non interpretabile come probabilità")

        # Se modello ritorna percentuale 0..100 -> normalizziamo
        if prob > 1.0 and prob <= 100.0:
            prob = prob / 100.0

        prob = max(0.0, min(1.0, prob))
        return prob