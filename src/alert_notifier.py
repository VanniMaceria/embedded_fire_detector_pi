import json
import logging
import paho.mqtt.client as mqtt

DEPLOYMENT = False

try:
    import RPi.GPIO as GPIO
    import board
    DEPLOYMENT = True
except:
    import mocks.GPIO as GPIO
    import mocks.board as board

logging.basicConfig(level=logging.INFO)


class AlertNotifier:
    """Gestisce la comunicazione con il server esterno."""
    BUZZER_PIN = 20

    def __init__(self):
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.BUZZER_PIN, GPIO.OUT)

        self.mqtt_server = "127.0.0.1"
        self.mqtt_port = 1884
        self.mqtt_clientID = "FireDetectorES"
        self.mqtt_username = "FireDetectorUser"
        self.mqtt_password = "FireDetectorPassword"
        self.topic = "v1/devices/me/telemetry"

        self.is_alert_active = False
        self.client = mqtt.Client(client_id=self.mqtt_clientID)

        if self.mqtt_username:
            self.client.username_pw_set(self.mqtt_username, self.mqtt_password)

        self._connected = False
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect

        self.client.loop_start()
        try:
            attempts = 0
            max_attempts = 3
            while attempts < max_attempts and not self._connected:
                logging.info("Connecting to MQTT broker (attempt %d)...", attempts + 1)
                try:
                    self.client.connect(self.mqtt_server, self.mqtt_port, keepalive=60)
                except Exception:
                    logging.exception("MQTT connect exception")
                attempts += 1
        except Exception:
            logging.exception("MQTT initial connect failed")

    def _on_connect(self, rc):
        if rc == 0:
            self._connected = True
            logging.info("MQTT connected to %s:%s", self.mqtt_server, self.mqtt_port)
        else:
            logging.error("MQTT connection failed with rc=%s", rc)

    def _on_disconnect(self, rc):
        self._connected = False
        logging.info("MQTT disconnected (rc=%s)", rc)

    def publish_via_mqtt(self, timestamp: str, confidence: float) -> bool:
        """
        Invia un messaggio MQTT con la forma:
        {"status":"FIRE_DETECTED","timestamp":"...","probability":...}
        """
        data = {
            "status": "FIRE_DETECTED",
            "timestamp": timestamp,
            "probability": confidence
        }

        payload = json.dumps(data)
        try:
            if not self._connected:
                try:
                    self.client.reconnect()
                except Exception:
                    logging.exception("Reconnect failed before publish")

            self.client.publish(self.topic, payload)
            logging.info("Published alert to %s: %s", self.topic, payload)
            return True
        except Exception:
            logging.exception("Publish failed")
            return False

    def notify(self, fire_detected: bool, timestamp: str, confidence: float):
        """
        Gestisce la logica di stato per evitare spam.
        """
        if fire_detected:   # Se viene rilevato un incendio
            if not self.is_alert_active:    # E non è stato mandato l'avviso, pubblica su MQTT
                self.publish_via_mqtt(timestamp, confidence)
                self.is_alert_active = True
                GPIO.output(self.BUZZER_PIN, GPIO.HIGH)
            # Se c'è fuoco e la notifica è stata già inviata non fare niente

        else:   # In assenza di incendio la notifica deve essere posta a falso
            self.is_alert_active = False
            GPIO.output(self.BUZZER_PIN, GPIO.LOW)
