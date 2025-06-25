import os
from cryptography.fernet import Fernet
from dotenv import load_dotenv

# Load environment variables from api.env file
load_dotenv("api.env")

_key = None
_fernet = None

def _load_key():
    key = os.getenv("NOTE_ENCRYPTION_KEY")
    if not key:
        raise EnvironmentError("NOTE_ENCRYPTION_KEY not set")
    return key.encode('utf-8')

def ensure_key_loaded():
    global _key, _fernet
    if _fernet is None:
        _key = _load_key()
        _fernet = Fernet(_key)
    return _fernet

def encrypt_content(content: str) -> str:
    fernet = ensure_key_loaded()
    return fernet.encrypt(content.encode('utf-8')).decode('utf-8')

def decrypt_content(encrypted_content: str) -> str:
    fernet = ensure_key_loaded()
    return fernet.decrypt(encrypted_content.encode('utf-8')).decode('utf-8')