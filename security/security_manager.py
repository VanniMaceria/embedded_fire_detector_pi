import json
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad


class SecurityManager:
    """Gestisce la crittografia dei dati sensibili."""

    def __init__(self, key):
        # La chiave deve essere di 16, 24 o 32 caratteri per AES
        self.key = key.encode('utf-8')
        self.block_size = AES.block_size

    def encrypt_data(self, data_dict):
        """Converte un dizionario in JSON e lo cripta in AES-256 ECB."""
        try:
            # 1. Converti dizionario in stringa JSON
            json_text = json.dumps(data_dict)

            # 2. Crea il cifratore AES (Modalità ECB)
            cipher = AES.new(self.key, AES.MODE_ECB)

            # 3. Applica il padding e cripta
            padded_data = pad(json_text.encode('utf-8'), self.block_size)
            encrypted_bytes = cipher.encrypt(padded_data)

            # 4. Restituisci in Base64 per l'invio via MQTT
            return base64.b64encode(encrypted_bytes).decode('utf-8')
        except Exception as e:
            print(f"Errore durante la crittografia: {e}")
            return None