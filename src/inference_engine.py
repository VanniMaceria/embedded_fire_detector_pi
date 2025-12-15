import numpy as np

class InferenceEngine:
    """Wrapper per il modello TFLite."""

    def __init__(self, model_path: str):
        # Qui caricheremo il TFLite Interpreter
        pass

    def predict(self, processed_image: np.ndarray) -> float:
        """
        Esegue l'inferenza.
        Restituisce un valore float tra 0.0 e 1.0 (confidenza incendio).
        """
        pass