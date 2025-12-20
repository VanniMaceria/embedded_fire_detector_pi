class AlertNotifier:
    """Gestisce la comunicazione con il server esterno."""

    def __init__(self, broker: str, topic: str):
        pass

    def send_alert(self, timestamp: str, confidence: float) -> bool:
        """
        Invia una messaggio MQTT via RestAPI
        Restituisce True se l'invio ha successo.
        """
        pass