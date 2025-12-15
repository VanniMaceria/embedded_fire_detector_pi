import numpy as np

class ImageProcessor:
    """Gestisce il preprocessing (resize, normalizzazione) e difese contro adversarial attacks."""

    def __init__(self, target_size: tuple = (224, 224)):
        self.target_size = target_size

    def preprocess(self, image: np.ndarray) -> np.ndarray:
        """
        Trasforma l'immagine raw in un formato accettabile dal modello.
        Qui potrai inserire filtri difensivi (es. Gaussian Blur) in futuro.
        """
        pass