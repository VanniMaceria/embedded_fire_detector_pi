import logging
import paho.mqtt.client as mqtt
import time

from security.security_manager import SecurityManager
from security import key as key

try:
    import RPi.GPIO as GPIO
    GPIO_MOCK = False
except (ImportError, RuntimeError):
    import mocks.GPIO as GPIO
    GPIO_MOCK = True

try:
    import board
except (ImportError, RuntimeError):
    import mocks.board as board

DEPLOYMENT = not GPIO_MOCK

# Configurazione logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')


class AlertNotifier:
    """Gestisce l'allarme acustico e la comunicazione MQTT con il broker."""

    def __init__(self):
        # Configurazione Hardware (Pin BCM 17 / Fisico 11)
        self.BUZZER_PIN = 17
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.BUZZER_PIN, GPIO.OUT)

        if GPIO_MOCK:
            logging.warning("ATTENZIONE: Modulo RPi.GPIO non trovato. Il buzzer FISICO non suonerà (MODALITÀ MOCK).")
        else:
            logging.info("Hardware GPIO rilevato. Allarme fisico pronto.")

        self.pwm = GPIO.PWM(self.BUZZER_PIN, 440)

        #Parametri di Rete
        self.mqtt_server = "127.0.0.1"
        self.mqtt_port = 1883
        self.mqtt_clientID = "FireDetectorES"
        self.mqtt_username = "FireDetectorUser"
        self.mqtt_password = "FireDetectorPassword"
        self.topic = "v1/devices/me/telemetry"

        # Parametri crittografia - usa una chiave da 32 caratteri per AES-256
        self.secret_key = key.AES_KEY
        self.security = SecurityManager(self.secret_key)

        # Stato Allarme e Timer
        self.is_alert_active = False
        self.last_alarm_trigger_time = 0  # Ultimo istante in cui è stato visto il fuoco
        self.min_alarm_duration = 2.0  # Durata minima allarme in secondi
        self._connected = False

        # Configurazione Client MQTT
        self.client = mqtt.Client(client_id=self.mqtt_clientID)
        if self.mqtt_username:
            self.client.username_pw_set(self.mqtt_username, self.mqtt_password)

        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect

        # Avvio MQTT Asincrono (Non blocca se il container è spento)
        try:
            logging.info("Inizializzazione MQTT asincrona...")
            self.client.connect_async(self.mqtt_server, self.mqtt_port, keepalive=60)
            self.client.loop_start()
        except Exception as e:
            logging.error(f"Errore setup MQTT: {e}")

    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self._connected = True
            logging.info(f"MQTT Connesso con successo alla porta {self.mqtt_port}")
        else:
            logging.error(f"Connessione MQTT fallita (codice: {rc})")

    def _on_disconnect(self, client, userdata, rc):
        self._connected = False
        logging.warning("Scollegato dal broker MQTT")

    def publish_via_mqtt(self, timestamp: str, confidence: float):
        """Prepara i dati, li fa criptare e li invia."""
        if not self._connected:
            return

        # Dati in chiaro
        data = {
            "status": "FIRE_DETECTED",
            "timestamp": timestamp,
            "probability": round(confidence, 4)
        }

        # crittografia dei dati
        payload_criptato = self.security.encrypt_data(data)

        if payload_criptato:
            self.client.publish(self.topic, payload_criptato)
            logging.info(f"Dati criptati inviati: {payload_criptato}")

        return True

    def notify(self, fire_detected: bool, timestamp: str, confidence: float):
        """Gestisce l'attivazione del buzzer e la logica di mantenimento."""
        current_time = time.time()

        if fire_detected:
            # Aggiorna il timestamp ogni volta che viene rilevato fuoco
            self.last_alarm_trigger_time = current_time

            if not self.is_alert_active:    # Caso in cui l'allarme non è ancora attivo
                logging.info("!!! ALLARME FISICO AVVIATO !!!")
                self.pwm.start(50)  # Duty cycle 50% per buzzer passivo
                self.is_alert_active = True
                self.publish_via_mqtt(timestamp, confidence)

        else:   # Caso in cui non c'è fuoco
            if self.is_alert_active:    # Se l'allarme è ancora attivo
                elapsed = current_time - self.last_alarm_trigger_time

                if elapsed >= self.min_alarm_duration:  #... E sono passati almeno 2 secondi, puoi spegnere l'allarme
                    logging.info(f"Spegnimento allarme dopo {elapsed:.1f}s di sicurezza.")
                    self.pwm.stop()
                    self.is_alert_active = False
                else:
                    pass

    def cleanup(self):
        """Rilascia le risorse GPIO."""
        self.pwm.stop()
        GPIO.cleanup()
        self.client.loop_stop()
        logging.info("Risorse AlertNotifier rilasciate.")
