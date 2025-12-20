from unittest import TestCase
from unittest.mock import patch, MagicMock
import paho.mqtt.client as mqtt
from src.alert_notifier import AlertNotifier
from unittest.mock import ANY
import mocks.GPIO as GPIO


class TestAlertNotifier(TestCase):

    @patch.object(mqtt, 'Client')  # Mocka la classe Client dentro il modulo mqtt
    def test_connects_to_broker_on_init(self, mock_client_class):
        # --- ARRANGE ---
        mock_instance = MagicMock()
        mock_client_class.return_value = mock_instance

        broker_ip = "192.168.1.100"

        # --- ACT ---
        notifier = AlertNotifier(broker=broker_ip, topic="allarme/incendio")  # Test del costruttore

        # --- ASSERT ---
        # Verifichiamo che il metodo connect dell'istanza sia stato chiamato col broker giusto
        mock_instance.connect.assert_called_once_with(broker_ip)


    @patch.object(mqtt, 'Client')
    def test_publish_via_mqtt_publishes_at_right_topic(self, mock_client_class):
        # --- ARRANGE ---
        mock_instance = MagicMock()
        mock_client_class.return_value = mock_instance

        topic = "allarme/incendio"
        notifier = AlertNotifier(broker="192.168.1.100", topic=topic)

        # --- ACT ---
        outcome = notifier.publish_via_mqtt(timestamp="2025-12-20 20:12:00", confidence=0.85)

        # --- ASSERT ---
        mock_instance.publish.assert_called_once_with(topic, ANY)
        self.assertTrue(outcome)

    @patch.object(mqtt, 'Client')
    def test_notify_does_not_send_mqtt_pub_multiple_times_when_fire_is_detected(self, mock_client_class):
        # --- ARRANGE ---
        mock_instance = MagicMock()
        mock_client_class.return_value = mock_instance

        notifier = AlertNotifier(broker="localhost", topic="test")

        # Stato iniziale: False
        self.assertFalse(notifier.is_alert_active)

        # --- ACT 1: PRIMO RILEVAMENTO (Fuoco SI) ---
        notifier.notify(fire_detected=True, timestamp="10:00:00", confidence=0.90)

        # --- ASSERT 1 ---
        # Controllo Stato: Deve essere attivo
        self.assertTrue(notifier.is_alert_active)
        # Controllo Comportamento: Il messaggio deve essere partito davvero
        mock_instance.publish.assert_called_once()

        # --- RESET MOCK ---
        # Puliamo la memoria del mock per il prossimo step
        mock_instance.publish.reset_mock()

        # --- ACT 2: RILEVAMENTO CONSECUTIVO (Fuoco SI) ---
        notifier.notify(fire_detected=True, timestamp="10:00:01", confidence=0.92)

        # --- ASSERT 2 ---
        # Controllo Stato: Deve rimanere attivo
        self.assertTrue(notifier.is_alert_active)
        # Controllo Comportamento: NON deve inviare nulla (evita spam)
        mock_instance.publish.assert_not_called()

    @patch.object(mqtt, 'Client')
    def test_resets_alert_state_when_fire_is_no_longer_detected(self, mock_client_class):
        # --- ARRANGE ---
        mock_client_class.return_value = MagicMock()
        notifier = AlertNotifier(broker="localhost", topic="test")

        notifier.is_alert_active = True

        # --- ACT ---
        notifier.notify(fire_detected=False, timestamp="12:00:00", confidence=0.0)

        # --- ASSERT ---
        # Verifichiamo che lo stato sia tornato False
        self.assertFalse(notifier.is_alert_active)


    @patch('src.alert_notifier.mqtt.Client')
    @patch.object(GPIO, "output")
    def test_buzzer_is_ringing_when_fire_is_detected(self, mock_buzzer, mock_mqtt_class):
        # --- ARRANGE ---
        mock_mqtt_class.return_value = MagicMock()

        notifier = AlertNotifier(broker="localhost", topic="test")

        # --- ACT ---
        notifier.notify(fire_detected=True, timestamp="12:00:00", confidence=0.9)

        # --- ASSERT ---
        self.assertTrue(notifier.is_alert_active)   # Output indiretto
        mock_buzzer.assert_called_once_with(notifier.BUZZER_PIN, True)    # Output diretto

    @patch('src.alert_notifier.mqtt.Client')
    @patch.object(GPIO, "output")
    def test_buzzer_is_turned_off_when_fire_is_not_detected(self, mock_buzzer, mock_mqtt_class):
        # --- ARRANGE ---
        mock_mqtt_class.return_value = MagicMock()

        notifier = AlertNotifier(broker="localhost", topic="test")
        notifier.is_alert_active = True

        # --- ACT ---
        notifier.notify(fire_detected=False, timestamp="12:00:00", confidence=0.9)

        # --- ASSERT ---
        self.assertFalse(notifier.is_alert_active)  # Output indiretto
        mock_buzzer.assert_called_once_with(notifier.BUZZER_PIN, False)  # Output diretto

