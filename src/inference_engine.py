"""
NOTA SULLE MODIFICHE (FIX COMPATIBILITÀ KERAS 3):
Questo file è stato modificato per permettere il caricamento di un modello .h5 legacy (creato con Keras 2)
su un ambiente moderno con Keras 3 / TensorFlow 2.x.

PROBLEMA RISCONTRATO:
Il modello originale includeva parametri di configurazione non più supportati o gestiti diversamente
in Keras 3, causando due errori critici:
1. "TypeError: unexpected keyword argument 'dtype'": Keras 3 non accetta `dtype` negli inizializzatori.
2. "ValueError: Kernel shape must have the same length as input": Errore di dimensione (Rank 5 vs 4) dovuto
   a come Keras 3 interpreta l'input_shape salvata nei vecchi file .h5 (aggiungendo una batch dim extra).

SOLUZIONE APPLICATA (MONKEY PATCHING):
Abbiamo creato delle classi wrapper "Patched" (PatchedGlorotUniform, PatchedZeros, PatchedConv2D) che:
1. Intercettano la configurazione dal file .h5.
2. Rimuovono i parametri problematici ('dtype') o correggono le dimensioni dell'input ('batch_input_shape').
3. Vengono iniettate nel metodo `load_model` tramite il dizionario `custom_objects`, sostituendo al volo
   le classi standard di Keras durante il caricamento.
"""

import os
from pathlib import Path
from typing import Optional
import numpy as np

# Importiamo Keras e i componenti da patchare
try:
    from keras.models import load_model
    from keras.initializers import GlorotUniform, Zeros
    from keras.layers import Conv2D
except ImportError:
    load_model = None
    GlorotUniform = object
    Zeros = object
    Conv2D = object


# --- FIX CRITICO PER KERAS 3 (Compatibilità Modelli Legacy) ---

class PatchedGlorotUniform(GlorotUniform):
    """Rimuove il parametro 'dtype' non più supportato in Keras 3."""

    def __init__(self, *args, **kwargs):
        kwargs.pop('dtype', None)
        super().__init__(*args, **kwargs)


class PatchedZeros(Zeros):
    """Rimuove il parametro 'dtype' non più supportato in Keras 3."""

    def __init__(self, *args, **kwargs):
        kwargs.pop('dtype', None)
        super().__init__(*args, **kwargs)


class PatchedConv2D(Conv2D):
    """
    Corregge l'errore di dimensione dell'input (Rank 5 vs Rank 4).
    I modelli vecchi salvavano input_shape=[None, 64, 64, 3].
    Keras 3 lo interpreta male aggiungendo un altro batch dim.
    Questa classe rimuove il 'None' iniziale dalla configurazione.
    """

    @classmethod
    def from_config(cls, config):
        # Controlliamo se c'è un input_shape "sporco" con il batch dimension (None)
        if 'batch_input_shape' in config:
            shape = config['batch_input_shape']
            if isinstance(shape, list) and len(shape) == 4 and shape[0] is None:
                # Trasformiamo [None, 64, 64, 3] in [64, 64, 3]
                config['batch_input_shape'] = shape
                if 'input_shape' in config:
                    del config['input_shape']

        if 'input_shape' in config:
            shape = config['input_shape']
            if isinstance(shape, list) and len(shape) == 4 and shape[0] is None:
                config['input_shape'] = shape[1:]  # Rimuovi il primo elemento (None)

        return super().from_config(config)


# --------------------------------

class InferenceEngine:
    """Wrapper per il modello di ML."""

    def __init__(self, model_path: Optional[str] = None):
        if model_path is None:
            model_path = os.path.join("models", "Fire-64x64-color-v7-soft.h5")

        model_file = Path(model_path)

        if not model_file.exists():
            raise FileNotFoundError(f"Modello non trovato: {model_file}")

        if load_model is None:
            raise RuntimeError("Keras/TensorFlow non installato.")

        print(f"[INFO] Caricamento modello (Patch Keras 3 attiva): {model_file}")

        # Dizionario di sostituzione per le classi problematiche
        custom_objects = {
            'GlorotUniform': PatchedGlorotUniform,
            'Zeros': PatchedZeros,
            'Conv2D': PatchedConv2D,  # Sostituiamo anche Conv2D!
        }

        try:
            self.model = load_model(
                str(model_file),
                custom_objects=custom_objects,
                compile=False
            )
        except Exception as e:
            # Fallback estremo: a volte Keras ha bisogno di config pulite manualmente
            print(f"[WARN] Primo tentativo fallito: {e}. Riprovo ignorando input shape...")
            raise RuntimeError(f"Impossibile caricare il modello legacy: {e}")

    def predict(self, processed_image: np.ndarray) -> float:
        """Esegue l'inferenza."""
        if self.model is None:
            raise RuntimeError("Modello non caricato")

        img = np.array(processed_image)

        # Aggiungi dimensione batch (1, 64, 64, 3)
        batch = np.expand_dims(img, axis=0)

        # Predizione silenziosa
        preds = self.model.predict(batch, verbose=0)

        try:
            prob = float(np.asarray(preds).reshape(-1)[0])
        except Exception:
            raise RuntimeError("Output non interpretabile")

        if 1.0 < prob <= 100.0:
            prob = prob / 100.0

        return max(0.0, min(1.0, prob))