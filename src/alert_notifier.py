import paho.mqtt.client as mqtt
import json

class AlertNotifier:
    """Gestisce la comunicazione con il server esterno."""

    def __init__(self, broker: str, topic: str):
        self.broker = broker
        self.topic = topic

        self.is_alert_active = False    # Stato interno: serve ancora per non mandare 1000 messaggi al secondo
        self.client = mqtt.Client()
        self.client.connect(self.broker)    # Prova a connettersi quando si chiama il costruttore
        self.BUZZER_PIN = 20

    def publish_via_mqtt(self, timestamp: str, confidence: float) -> bool:
        """
        Invia una messaggio MQTT
        Restituisce True se l'invio ha successo.
        """

        data = {
            "status": "FIRE_DETECTED",
            "timestamp": timestamp,
            "probability": confidence
        }

        payload = json.dumps(data)    # Converte in stringa JSON
        self.client.publish(self.topic, payload)     # Invia al broker

        return True

    def notify(self, fire_detected: bool, timestamp: str, confidence: float):
        """
        Gestisce la logica di stato per evitare spam.
        """
        if fire_detected:   # Se viene rilevato un incendio
            if not self.is_alert_active:    # E non è stato mandato l'avviso, pubblica su MQTT
                self.publish_via_mqtt(timestamp, confidence)
                self.is_alert_active = True
            # Se c'è fuoco e la notifica è stata già inviata non fare niente

        else:   # In assenza di incendio la notifica deve essere posta a falso
            self.is_alert_active = False
