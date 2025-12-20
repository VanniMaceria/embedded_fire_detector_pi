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

    @patch.object(ie_module, 'load_model')
    def test_predict_calls_returns_float(self, mock_load_model):
        """Verifica che `predict` chiami `model.predict` e ritorni una float probability."""
        fake_model = MagicMock()
        fake_model.predict.return_value = np.array([[0.8]])
        mock_load_model.return_value = fake_model

        engine = ie_module.InferenceEngine(model_path="models/dummy.h5")
        img = np.random.randint(0, 256, size=(64, 64, 3), dtype=np.uint8)

        prob = engine.predict(img)

        self.assertIsInstance(prob, float)
        self.assertGreaterEqual(prob, 0.0)
        self.assertLessEqual(prob, 1.0)
        fake_model.predict.assert_called()

        call_args = fake_model.predict.call_args
        self.assertIsNotNone(call_args)
        batch_arg = call_args[0][0]
        self.assertEqual(batch_arg.shape, (1, 64, 64, 3))