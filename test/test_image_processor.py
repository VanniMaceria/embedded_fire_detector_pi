from unittest import TestCase
import numpy as np

from src.image_processor import ImageProcessor


class TestImageProcessor(TestCase):
    def test_preprocess_resizes_and_normalizes(self):
        # ARRANGE: immagine di input casuale in uint8 con dimensione non 64x64
        img = np.random.randint(0, 256, size=(120, 200, 3), dtype=np.uint8)
        proc = ImageProcessor()  # default target_size dovrebbe essere 64x64

        # ACT
        out = proc.preprocess(img)

        # ASSERT: dimensione, tipo e range di valori
        self.assertIsInstance(out, np.ndarray)
        self.assertEqual(out.shape, (64, 64, 3))
        self.assertTrue(np.issubdtype(out.dtype, np.floating))
        self.assertGreaterEqual(out.min(), 0.0)
        self.assertLessEqual(out.max(), 1.0)