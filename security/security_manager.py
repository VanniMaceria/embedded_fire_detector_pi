import json
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from Crypto.Random import get_random_bytes


class SecurityManager:
    def __init__(self, key):
        self.key = key.encode('utf-8')
        self.block_size = AES.block_size

    def encrypt_data(self, data_dict):
        """Cripta i dati in AES-256 CBC con IV casuale."""
        try:
            json_text = json.dumps(data_dict).encode('utf-8')

            # 1. Genera un IV casuale di 16 byte
            iv = get_random_bytes(16)

            # 2. Crea il cifratore in modalità CBC
            cipher = AES.new(self.key, AES.MODE_CBC, iv)

            # 3. Applica il padding e cripta
            padded_data = pad(json_text, self.block_size)
            encrypted_bytes = cipher.encrypt(padded_data)

            # 4. Concatena IV + Dati Criptati e codifica in Base64
            # L'IV deve stare all'inizio per permettere la decriptazione
            return base64.b64encode(iv + encrypted_bytes).decode('utf-8')
        except Exception as e:
            print(f"Errore durante la crittografia: {e}")
            return None