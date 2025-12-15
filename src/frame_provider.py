import numpy as np

class FrameProvider:
    """Gestisce l'acquisizione delle immagini dalla camera hardware."""

    def __init__(self, resolution: tuple = (640, 480)):
        # Qui inizializzeremo la PiCamera
        pass

    def get_frame(self) -> np.ndarray:
        """Cattura un frame e lo restituisce come array NumPy."""
        pass