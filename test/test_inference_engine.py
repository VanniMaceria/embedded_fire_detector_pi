from unittest import TestCase
from unittest.mock import patch, MagicMock
import numpy as np
import src.inference_engine as ie_module


class TestInferenceEngine(TestCase):
    @patch.object(ie_module, 'load_model')
    def test_loads_model_with_given_path(self, mock_load_model):
        """Verifica che `load_model` venga chiamato con il percorso fornito."""
        fake_model = MagicMock()
        mock_load_model.return_value = fake_model

        ie_module.InferenceEngine(model_path="models/dummy.h5")

        mock_load_model.assert_called_once_with("models/dummy.h5")