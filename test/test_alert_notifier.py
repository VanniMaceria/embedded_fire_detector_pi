from unittest import TestCase
from unittest.mock import patch, MagicMock, ANY
import paho.mqtt.client as mqtt
from src.alert_notifier import AlertNotifier
import mocks.GPIO as GPIO


class TestAlertNotifier(TestCase):

    @patch.object(mqtt, 'Client')
    def test_connects_to_broker_on_init(self, mock_client_class):
        # --- ARRANGE ---
        mock_instance = MagicMock()
        mock_client_class.return_value = mock_instance

        # --- ACT ---
        notifier = AlertNotifier()

        # --- ASSERT ---
        mock_instance.connect.assert_called_with("127.0.0.1", 1884, keepalive=60)

    @patch.object(mqtt, 'Client')
    def test_publish_via_mqtt_publishes_at_right_topic(self, mock_client_class):
        # --- ARRANGE ---
        mock_instance = MagicMock()
        mock_client_class.return_value = mock_instance
        notifier = AlertNotifier()

        # Simuliamo che la connessione sia attiva, altrimenti publish_via_mqtt fallisce
        notifier._connected = True

        # --- ACT ---
        outcome = notifier.publish_via_mqtt(timestamp="2025-12-20 20:12:00", confidence=0.85)

        # --- ASSERT ---
        mock_instance.publish.assert_called_once_with("v1/devices/me/telemetry", ANY)
        self.assertTrue(outcome)

    @patch.object(mqtt, 'Client')
    def test_notify_does_not_send_mqtt_pub_multiple_times_when_fire_is_detected(self, mock_client_class):
        # --- ARRANGE ---
        mock_instance = MagicMock()
        mock_client_class.return_value = mock_instance
        notifier = AlertNotifier()
        notifier._connected = True

        # --- ACT 1: PRIMO RILEVAMENTO ---
        notifier.notify(fire_detected=True, timestamp="10:00:00", confidence=0.90)

        # --- ASSERT 1 ---
        self.assertTrue(notifier.is_alert_active)
        mock_instance.publish.assert_called_once()

        # --- RESET MOCK ---
        mock_instance.publish.reset_mock()

        # --- ACT 2: RILEVAMENTO CONSECUTIVO ---
        notifier.notify(fire_detected=True, timestamp="10:00:01", confidence=0.92)

        # --- ASSERT 2 ---
        # Non deve chiamare publish una seconda volta (meccanismo anti-spam)
        mock_instance.publish.assert_not_called()

    @patch.object(mqtt, 'Client')
    def test_resets_alert_state_when_fire_is_no_longer_detected(self, mock_client_class):
        # --- ARRANGE ---
        mock_instance = MagicMock()
        mock_client_class.return_value = mock_instance
        notifier = AlertNotifier()
        notifier.is_alert_active = True

        # --- ACT ---
        notifier.notify(fire_detected=False, timestamp="12:00:00", confidence=0.0)

        # --- ASSERT ---
        self.assertFalse(notifier.is_alert_active)

    @patch('src.alert_notifier.mqtt.Client')
    @patch.object(GPIO, "output")
    def test_buzzer_is_ringing_when_fire_is_detected(self, mock_buzzer, mock_mqtt_class):
        # --- ARRANGE ---
        mock_mqtt_class.return_value = MagicMock()
        notifier = AlertNotifier()
        notifier._connected = True

        # --- ACT ---
        notifier.notify(fire_detected=True, timestamp="12:00:00", confidence=0.9)

        # --- ASSERT ---
        mock_buzzer.assert_called_once_with(notifier.BUZZER_PIN, GPIO.HIGH)

    @patch('src.alert_notifier.mqtt.Client')
    @patch.object(GPIO, "output")
    def test_buzzer_is_turned_off_when_fire_not_detected(self, mock_buzzer, mock_mqtt_class):
        # --- ARRANGE ---
        mock_mqtt_class.return_value = MagicMock()
        notifier = AlertNotifier()
        notifier.is_alert_active = True

        # --- ACT ---
        notifier.notify(fire_detected=False, timestamp="12:00:00", confidence=0.9)

        # --- ASSERT ---
        mock_buzzer.assert_called_once_with(notifier.BUZZER_PIN, GPIO.LOW)