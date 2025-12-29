import cv2
import numpy as np
from src.exceptions.FrameError import FrameError

class ImageProcessor:
    """
    Preprocessing standard per MobileNetV2:
    - Resize 224x224
    - Colore RGB
    - Normalizzazione [0, 1]
    """
    def __init__(self, target_size: tuple = (224, 224)):
        self.target_size = target_size

    def preprocess(self, image: np.ndarray) -> np.ndarray:
        if image is None:
            raise FrameError("Frame vuoto")

        img = np.array(image)

        # 1. BGR -> RGB
        if img.ndim == 3 and img.shape[2] == 3:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        elif img.ndim == 2: # Se per caso è scala di grigi
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)

        # 2. Resize
        img = cv2.resize(img, self.target_size, interpolation=cv2.INTER_AREA)

        # 3. Normalizzazione
        img = img.astype("float32") / 255.0

        return img