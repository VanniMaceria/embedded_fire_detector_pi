import cv2
import argparse
from datetime import datetime
import time
from collections import deque
import numpy as np

from src.frame_provider import FrameProvider
from src.image_processor import ImageProcessor
from src.inference_engine import InferenceEngine
from src.alert_notifier import AlertNotifier


class FireMonitor:
    def __init__(self, video_path: str, model_path: str):
        print(f"[INFO] Avvio Sistema Antincendio...")

        self.inference_engine = InferenceEngine(model_path=model_path)
        self.alert_notifier = AlertNotifier()

        req_w = getattr(self.inference_engine, 'width', 224)
        req_h = getattr(self.inference_engine, 'height', 224)
        print(f"[INFO] Modello caricato. Configuro ImageProcessor su: {req_w}x{req_h}")

        self.image_processor = ImageProcessor(target_size=(req_w, req_h))

        self.frame_provider = FrameProvider(path=video_path)

        # determina l'FPS del video sorgente (fallback 25)
        cap = getattr(self.frame_provider, "capturer", None)
        try:
            src_fps = float(cap.get(cv2.CAP_PROP_FPS)) if cap is not None else 0.0
        except Exception:
            src_fps = 0.0
        self.target_fps = src_fps if src_fps and src_fps > 0.0 else 25.0
        print(f"[INFO] FPS sorgente: {src_fps:.2f} -> target_fps: {self.target_fps:.2f}")

        self.is_running = True
        # soglia in 0..1
        self.threshold = 0.70

        # smoothing buffer (valori 0..1)
        self.window_size = 5
        self.prob_buffer = deque(maxlen=self.window_size)

    def run(self):
        """
        Ciclo principale di monitoraggio.
        """
        print("[INFO] Monitoraggio attivo. Premi 'q' sulla finestra video per uscire.")
        try:
            while self.is_running:
                loop_start = time.time()
                # 1. Acquisisci Frame
                frame = self.frame_provider.get_frame()
                if frame is None:
                    print("[INFO] Flusso video terminato.")
                    break

                # 2. Preprocessa (Resize, RGB, 0-1)
                input_tensor = self.image_processor.preprocess(frame)

                # 3. Inferenza (Ritorna probabilità incendio 0.0 - 1.0)
                start = time.time()
                confidence = self.inference_engine.predict(input_tensor)
                end = time.time()

                # calcolo FPS inferenza (può essere volatile)
                fps = 1.0 / max((end - start), 1e-6)

                # 4. Smoothing: mantengo buffer di probabilità (0..1)
                self.prob_buffer.append(confidence)
                avg_confidence = float(np.mean(self.prob_buffer)) if len(self.prob_buffer) > 0 else confidence

                # 5. Logica decisionale usando la media
                is_fire = avg_confidence > self.threshold
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                # 6. Notifica (MQTT + Buzzer) - invio la conf. media
                self.alert_notifier.notify(
                    fire_detected=is_fire,
                    timestamp=timestamp,
                    confidence=avg_confidence
                )

                # 7. Visualizzazione a schermo (passo fps e media)
                self._display_frame(frame, is_fire, avg_confidence, fps)

                # Limitare il framerate al FPS del file (o fallback) e gestire uscita
                loop_elapsed = time.time() - loop_start
                target_interval = 1.0 / float(self.target_fps)
                remaining = target_interval - loop_elapsed
                wait_ms = int(max(1, remaining * 1000)) if remaining > 0 else 1
                if cv2.waitKey(wait_ms) & 0xFF == ord('q'):
                    self.stop()

        except KeyboardInterrupt:
            print("\n[INFO] Interruzione manuale.")
        except Exception as e:
            print(f"\n[ERRORE] {e}")
            import traceback
            traceback.print_exc()
        finally:
            self._cleanup()

    def _display_frame(self, frame, is_fire, confidence, fps=0.0):
        """Visualizza il frame con etichette, barra visiva e FPS."""
        display = frame.copy()
        h, w, _ = display.shape

        percent = confidence * 100.0

        # bordo
        color = (0, 0, 255) if is_fire else (0, 255, 0)
        thickness = 5 if is_fire else 2
        cv2.rectangle(display, (0, 0), (w, h), color, thickness)

        # testi: probabilità e FPS
        label = f"Fire: {percent:.2f}%"
        fps_label = f"FPS: {fps:.1f}"

        cv2.putText(display, label, (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        cv2.putText(display, fps_label, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)

        if is_fire:
            cv2.putText(display, "ALLARME INCENDIO", (10, 85), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 3)

        # barra visiva probabilità
        bar_x, bar_y = 10, 110
        bar_w, bar_h = 220, 20
        filled_w = int((percent / 100.0) * bar_w)
        cv2.rectangle(display, (bar_x, bar_y), (bar_x + bar_w, bar_y + bar_h), (200, 200, 200), 1)
        cv2.rectangle(display, (bar_x, bar_y), (bar_x + filled_w, bar_y + bar_h), (0, 0, 255), -1)

        cv2.imshow("Fire Monitor System", display)

    def stop(self):
        self.is_running = False

    def _cleanup(self):
        cv2.destroyAllWindows()
        print("[INFO] Risorse rilasciate.")


# --- MAIN ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--video", required=True, help="Percorso del video")
    parser.add_argument("--model", default="models/fire_model.tflite", help="Percorso del modello .tflite")
    #parser.add_argument("--broker", default="broker.emqx.io", help="Broker MQTT")
    #parser.add_argument("--topic", default="allarme/incendio", help="Topic MQTT")
    args = parser.parse_args()

    FireMonitor(args.video, args.model).run()