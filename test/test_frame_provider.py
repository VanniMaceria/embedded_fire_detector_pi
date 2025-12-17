import unittest
from unittest.mock import patch, MagicMock
import numpy as np
import cv2
from src.frame_provider import FrameProvider


class TestFrameProvider(unittest.TestCase):
    @patch.object(cv2, 'VideoCapture')
    def test_get_frame_returns_numpy_array(self, video_capture: MagicMock):
        # --- ARRANGE ---
        fake_frame = np.zeros((10, 10, 3), dtype=np.uint8)  # Crea un'immagine nera 10x10 pixel. Questo sarà il risultato atteso.
        mock_frame_taker = MagicMock()

        mock_frame_taker.read.return_value = (True, fake_frame)  # Quando si fa la read il metodo deve restituire la tupla (True, fake_frame)
        mock_frame_taker.isOpened.return_value = True  # Quando si verifica isOpened ritorna sempre True

        video_capture.return_value = mock_frame_taker  # cv2.VideoCapture() deve restituire il frame finto che è stato preparato sopra

        frame_provider = FrameProvider("percorso_dummy.mp4")

        # --- ACT ---
        result = frame_provider.get_frame()

        # --- ASSERT ---
        self.assertIsInstance(result, np.ndarray)  # Verifica che il frame letto sia un array nunmpy
        self.assertTrue(np.array_equal(result, fake_frame)) # Verifica che il frame sia proprio fake_frame