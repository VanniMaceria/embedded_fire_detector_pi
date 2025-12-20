import paho.mqtt.client as mqtt

class AlertNotifier:
    """Gestisce la comunicazione con il server esterno."""

    def __init__(self, broker: str, topic: str):
        self.broker = broker
        self.topic = topic

        self.is_alert_active = False    # Stato interno: serve ancora per non mandare 1000 messaggi al secondo
        self.client = mqtt.Client()
        self.client.connect(self.broker)    # Prova a connettersi quando si chiama il costruttore

    def send_alert(self, timestamp: str, confidence: float) -> bool:
        """
        Invia una messaggio MQTT
        Restituisce True se l'invio ha successo.
        """
        pass