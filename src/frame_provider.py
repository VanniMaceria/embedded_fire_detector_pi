import cv2
import numpy as np

from src.exceptions.VideoOpenError import VideoOpenError


class FrameProvider:
    """Gestisce l'acquisizione delle immagini dal video."""

    def __init__(self, path: str):
        self.capturer = cv2.VideoCapture(path)
        if not self.capturer.isOpened():
             raise VideoOpenError   # Se non riesce ad aprire il video dal path allora c'è un problema


    def get_frame(self) -> np.ndarray:
        """Cattura un frame e lo restituisce come array NumPy."""
        result = self.capturer.read()   # Restituisce l'esito (bool) e la matrice.
        #outcome = result[0]    # Restituisce falso quando il video è finito o non è riuscito a leggere il frame. Quando è così si fa ripartire il video per dare l'effetto loop
        frame = result[1]



        return frame