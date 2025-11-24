# utils.py
import io
import zipfile
from pathlib import Path
from cryptography.fernet import Fernet
import streamlit as st
import os

KEY_PATH = Path("secret.key")

def _get_key_from_secrets():
    """
    Retorna chave (bytes) definida em st.secrets['FERNET_KEY'] se existir.
    """
    try:
        key = st.secrets.get("FERNET_KEY")
        if key:
            return key.encode() if isinstance(key, str) else key
    except Exception:
        return None
    return None

def gerar_chave_local(save_path: Path = KEY_PATH) -> bytes:
    """
    Gera e salva secret.key localmente (apenas dev).
    """
    if save_path.exists():
        return save_path.read_bytes()
    key = Fernet.generate_key()
    save_path.write_bytes(key)
    return key

def carregar_chave() -> bytes:
    """
    Fluxo para obter key:
     1) st.secrets (preferido)
     2) secret.key local
     3) gerar secret.key local (dev)
    """
    key = _get_key_from_secrets()
    if key:
        return key
    if KEY_PATH.exists():
        return KEY_PATH.read_bytes()
    return gerar_chave_local(KEY_PATH)

# ----------------- compressão em memória -----------------
def compress_bytes_to_zip(data_bytes: bytes, filename_in_zip: str) -> bytes:
    """
    Retorna bytes de um ZIP (ZIP_DEFLATED) contendo filename_in_zip com o conteúdo data_bytes.
    """
    bio = io.BytesIO()
    with zipfile.ZipFile(bio, mode="w", compression=zipfile.ZIP_DEFLATED) as z:
        z.writestr(filename_in_zip, data_bytes)
    return bio.getvalue()

# ----------------- encrypt / decrypt --------------------
def encrypt_bytes_fernet(data: bytes, key: bytes = None) -> bytes:
    if key is None:
        key = carregar_chave()
    f = Fernet(key)
    return f.encrypt(data)

def decrypt_bytes_fernet(token: bytes, key: bytes = None) -> bytes:
    if key is None:
        key = carregar_chave()
    f = Fernet(key)
    return f.decrypt(token)


