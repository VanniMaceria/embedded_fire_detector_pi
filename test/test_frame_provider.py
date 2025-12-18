import unittest
from unittest.mock import patch, MagicMock
import numpy as np
import cv2
from src.exceptions.VideoOpenError import VideoOpenError
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
        self.assertIsInstance(result, np.ndarray)  # Verifica che il frame letto sia un n-dimensional array nunmpy
        self.assertTrue(np.array_equal(result, fake_frame)) # Verifica che il frame sia proprio fake_frame

    @patch.object(cv2, 'VideoCapture')
    def test_init_raises_exception_when_video_cannot_be_opened(self, video_capture: MagicMock):
        # --- ARRANGE ---
        mock_frame_taker = MagicMock()
        mock_frame_taker.isOpened.return_value = False
        video_capture.return_value = mock_frame_taker

        # --- ACT & ASSERT ---
        self.assertRaises(VideoOpenError, FrameProvider, "bad_path.mp4")    # Verifica che init() lanci l'eccezione

    @patch.object(cv2, 'VideoCapture')
    def test_get_frame_loops_video_when_it_ends(self, video_capture: MagicMock):
        # --- ARRANGE ---
        fake_frame = np.zeros((10, 10, 3), dtype=np.uint8)
        mock_frame_taker = MagicMock()
        mock_frame_taker.isOpened.return_value = True

        mock_frame_taker.read.side_effect = [(False, None), (True, fake_frame)]   # Verifica prima cosa accade con False e poi con True -> dovrebbe ripartire
        video_capture.return_value = mock_frame_taker

        frame_provider = FrameProvider("video.mp4")

        # --- ACT ---
        result = frame_provider.get_frame()

        # --- ASSERT ---
        self.assertTrue(np.array_equal(result, fake_frame))
        # cv2.CAP_PROP_POS_FRAMES è la proprietà che indica la posizione
        mock_frame_taker.set.assert_called_with(cv2.CAP_PROP_POS_FRAMES, 0)    # Verifica che la testina di lettura sia all'inizio (0)


