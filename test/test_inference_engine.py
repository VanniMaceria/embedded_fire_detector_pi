from unittest import TestCase
from unittest.mock import patch, MagicMock
import numpy as np
from mock.mock import ANY
import src.inference_engine as ie_module
from pathlib import Path


class TestInferenceEngine(TestCase):

    @patch.object(ie_module, 'load_model')
    @patch('pathlib.Path.exists')
    def test_loads_model_with_given_path(self, mock_exists, mock_load_model):
        """Verifica che `load_model` venga chiamato con il percorso fornito."""

        # --- ARRANGE ---
        mock_exists.return_value = True

        fake_model = MagicMock()
        mock_load_model.return_value = fake_model

        # --- ACT ---
        ie_module.InferenceEngine(model_path="models/dummy.h5")

        # --- ASSERT ---
        # Verifichiamo che load_model sia stato chiamato con il percorso corretto
        expected_path = str(Path("models/dummy.h5"))
        mock_load_model.assert_called_once_with(
            expected_path,
            custom_objects=ANY,
            compile=False
        )

    @patch.object(ie_module, 'load_model')
    @patch('pathlib.Path.exists')
    def test_predict_calls_returns_float(self, mock_exists, mock_load_model):
        """Verifica che `predict` chiami `model.predict` e ritorni una float probability."""

        # --- ARRANGE ---
        mock_exists.return_value = True  # Il file esiste

        fake_model = MagicMock()

        fake_model.predict.return_value = 0.8
        mock_load_model.return_value = fake_model

        engine = ie_module.InferenceEngine(model_path="models/dummy.h5")

        # Creiamo un'immagine random 64x64x3
        img = np.random.randint(0, 256, size=(64, 64, 3), dtype=np.uint8)

        # --- ACT ---
        prob = engine.predict(img)

        # --- ASSERT ---
        self.assertIsInstance(prob, float)
        self.assertGreaterEqual(prob, 0.0)
        self.assertLessEqual(prob, 1.0)

        # Verifichiamo che il modello abbia ricevuto un batch (1, 64, 64, 3)
        fake_model.predict.assert_called()
        call_args = fake_model.predict.call_args
        batch_arg = call_args[0][0]  # Il primo argomento della chiamata
        self.assertEqual(batch_arg.shape, (1, 64, 64, 3))