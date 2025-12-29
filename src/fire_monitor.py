import cv2
import argparse
from datetime import datetime

# Importiamo i tuoi moduli
from src.frame_provider import FrameProvider
from src.image_processor import ImageProcessor
from src.inference_engine import InferenceEngine
from src.alert_notifier import AlertNotifier


class FireMonitor:
    def __init__(self, video_path: str, model_path: str, broker_ip: str, topic: str):
        print(f"[INFO] Avvio Sistema Antincendio...")

        self.inference_engine = InferenceEngine(model_path=model_path)

        req_w = getattr(self.inference_engine, 'width', 224)
        req_h = getattr(self.inference_engine, 'height', 224)
        print(f"[INFO] Modello caricato. Configuro ImageProcessor su: {req_w}x{req_h}")

        self.image_processor = ImageProcessor(target_size=(req_w, req_h))

        self.frame_provider = FrameProvider(path=video_path)
        self.alert_notifier = AlertNotifier(broker=broker_ip, topic=topic)

        self.is_running = True
        self.threshold = 0.5

    def run(self):
        """
        Ciclo principale di monitoraggio.
        """
        print("[INFO] Monitoraggio attivo. Premi 'q' sulla finestra video per uscire.")
        try:
            while self.is_running:
                # 1. Acquisisci Frame
                frame = self.frame_provider.get_frame()
                if frame is None:
                    print("[INFO] Flusso video terminato.")
                    break

                # 2. Preprocessa (Resize, RGB, 0-1)
                input_tensor = self.image_processor.preprocess(frame)

                # 3. Inferenza (Ritorna probabilità incendio 0.0 - 1.0)
                # (Ricorda: InferenceEngine ora inverte il risultato 1.0 - val)
                confidence = self.inference_engine.predict(input_tensor)

                # 4. Logica Decisionale
                is_fire = confidence > self.threshold
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                # 5. Notifica (MQTT + Buzzer)
                self.alert_notifier.notify(is_fire, timestamp, confidence)

                # 6. Visualizzazione a schermo
                self._display_frame(frame, is_fire, confidence)

                # Gestione uscita (Tasto 'q')
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    self.stop()

        except KeyboardInterrupt:
            print("\n[INFO] Interruzione manuale.")
        except Exception as e:
            print(f"\n[ERRORE] {e}")
            import traceback
            traceback.print_exc()
        finally:
            self._cleanup()

    def _display_frame(self, frame, is_fire, confidence):
        display = frame.copy()
        h, w, _ = display.shape

        if is_fire:
            color = (0, 0, 255)  # Rosso
            text = f"ALLARME INCENDIO! ({confidence:.2f})"
            thickness = 5
        else:
            color = (0, 255, 0)  # Verde
            text = f"SICURO ({confidence:.2f})"
            thickness = 2

        # Bordo colorato
        cv2.rectangle(display, (0, 0), (w, h), color, thickness)

        # Sfondo nero per il testo (per leggibilità)
        (text_w, text_h), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)
        cv2.rectangle(display, (20, 20), (30 + text_w, 40 + text_h), (0, 0, 0), -1)

        # Scritta
        cv2.putText(display, text, (25, 35 + text_h), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

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

    # Default al tuo nuovo modello personalizzato
    parser.add_argument("--model", default="models/fire_model.tflite", help="Percorso del modello .tflite")

    parser.add_argument("--broker", default="broker.emqx.io", help="Broker MQTT")
    parser.add_argument("--topic", default="allarme/incendio", help="Topic MQTT")
    args = parser.parse_args()

    FireMonitor(args.video, args.model, args.broker, args.topic).run()