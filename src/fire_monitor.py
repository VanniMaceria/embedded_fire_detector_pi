from src.alert_notifier import AlertNotifier
from src.frame_provider import FrameProvider
from src.image_processor import ImageProcessor
from src.inference_engine import InferenceEngine

# non dimentichiamo di citare gli autori del modello
class FireMonitor:
    """
    Classe principale (Controller).
    Coordina le altre classi per eseguire il loop di monitoraggio.
    """

    def __init__(self,
                 frame_provider: FrameProvider,
                 image_processor: ImageProcessor,
                 inference_engine: InferenceEngine,
                 notifier: AlertNotifier):
        self.frame_provider = frame_provider
        self.image_processor = image_processor
        self.inference_engine = inference_engine
        self.notifier = notifier
        self.threshold = 0.75  # Soglia di attivazione

    def run_cycle(self):
        """
        Esegue un singolo ciclo di controllo:
        1. Prende il frame
        2. Processa
        3. Inferenza
        4. (Opzionale) Alert
        """
        pass