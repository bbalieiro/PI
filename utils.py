# utils.py
import os
import pyaes

KEY_FILE = "secret.key"

def gerar_chave():
    """
    Gera chave AES-256 e salva em secret.key.
    """
    if os.path.exists(KEY_FILE):
        return open(KEY_FILE, "rb").read()
    key = os.urandom(32)  # 32 bytes = AES-256
    open(KEY_FILE, "wb").write(key)
    return key

def carregar_chave():
    """
    Carrega chave existente ou gera uma nova.
    """
    if not os.path.exists(KEY_FILE):
        return gerar_chave()
    return open(KEY_FILE, "rb").read()

def encrypt_bytes(data: bytes, key: bytes = None) -> bytes:
    """
    Criptografa bytes com AES-CTR.
    """
    if key is None:
        key = carregar_chave()
    aes = pyaes.AESModeOfOperationCTR(key)
    return aes.encrypt(data)

def decrypt_bytes(data: bytes, key: bytes = None) -> bytes:
    """
    Descriptografa bytes com AES-CTR.
    """
    if key is None:
        key = carregar_chave()
    aes = pyaes.AESModeOfOperationCTR(key)
    return aes.decrypt(data)
