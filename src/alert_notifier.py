class AlertNotifier:
    """Gestisce la comunicazione con il server esterno."""

    def __init__(self, endpoint: str):
        self.endpoint = endpoint

    def send_alert(self, timestamp: str, confidence: float) -> bool:
        """
        Invia una POST via RestAPI
        Restituisce True se l'invio ha successo.
        """
        pass