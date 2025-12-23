import cv2
import numpy as np
from src.exceptions.FrameError import FrameError


class ImageProcessor:
    """
    Gestisce il preprocessing per la Fire Detection.
    Robusta contro input diversi (grayscale, float) e corretta per i colori (RGB).
    """

    def __init__(self, target_size: tuple = (64, 64)):
        self.target_size = target_size

    def preprocess(self, image: np.ndarray) -> np.ndarray:
        if image is None:
            raise FrameError("Tentativo di preprocessare un frame None")

        img = np.array(image)

        # Caso immagine Grayscale (2D o 3D a 1 canale) -> Converti in RGB
        if img.ndim == 2:
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
        elif img.ndim == 3 and img.shape[2] == 1:
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)

        # Caso immagine BGR (Standard OpenCV) -> Converti in RGB
        # (Assumiamo che se ha 3 canali sia BGR, che è lo standard di cv2.VideoCapture)
        elif img.ndim == 3 and img.shape[2] == 3:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        # RESIZE
        # Usiamo INTER_AREA per ridurre la perdita di qualità nel downscaling
        img_resized = cv2.resize(img, self.target_size, interpolation=cv2.INTER_AREA)

        # Se è intero (0-255), converti e dividi
        if not np.issubdtype(img_resized.dtype, np.floating):
            img_resized = img_resized.astype('float32') / 255.0
        # Se è già float, controlla se serve normalizzare
        else:
            img_resized = img_resized.astype('float32')
            if img_resized.max() > 1.0:
                img_resized /= 255.0

        return img_resized