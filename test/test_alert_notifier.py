from unittest import TestCase
from unittest.mock import patch, MagicMock
import paho.mqtt.client as mqtt
from src.alert_notifier import AlertNotifier


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