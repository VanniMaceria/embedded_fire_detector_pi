class AlertNotifier:
    """Gestisce la comunicazione con il server esterno."""

    def __init__(self, topic: str):
        self.topic = topic

    def send_alert(self, timestamp: str, confidence: float) -> bool:
        """
        Invia un messaggio con MQTT al broker.
        Restituisce True se l'invio ha successo.
        """
        pass