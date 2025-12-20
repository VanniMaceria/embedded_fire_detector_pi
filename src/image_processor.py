import cv2
import numpy as np

class ImageProcessor:
    """Gestisce il preprocessing (resize, normalizzazione) e difese contro adversarial attacks.

    Per il workflow del progetto il default `target_size` è 64x64.
    """

    def __init__(self, target_size: tuple = (64, 64)):
        # target_size come (width, height) per cv2.resize
        self.target_size = target_size

    def preprocess(self, image: np.ndarray) -> np.ndarray:
        """
        Trasforma l'immagine raw in un formato accettabile dal modello.

        Operazioni:
        - converti immagini grayscale a 3 canali
        - ridimensiona a `target_size`
        - normalizza in [0,1] e restituisce dtype float32
        """
        img = np.array(image)

        # Se immagine in scala di grigi (H,W) o (H,W,1), converti a BGR 3 canali
        if img.ndim == 2:
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        elif img.ndim == 3 and img.shape[2] == 1:
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

        # cv2.resize aspetta (width, height)
        width, height = self.target_size
        img_resized = cv2.resize(img, (width, height), interpolation=cv2.INTER_AREA)

        # Normalizza in [0,1] e cast a float32
        if not np.issubdtype(img_resized.dtype, np.floating):
            img_resized = img_resized.astype('float32') / 255.0
        else:
            img_resized = img_resized.astype('float32')
            if img_resized.max() > 1.0:
                img_resized = img_resized / 255.0

        return img_resized