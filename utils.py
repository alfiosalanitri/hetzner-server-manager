import os
from cryptography.fernet import Fernet
from flask import abort

ENCRYPTION_KEY = os.getenv('SECRET_ENCRYPTION_KEY')

if not ENCRYPTION_KEY:
    raise RuntimeError("SECRET_ENCRYPTION_KEY not set in .env! App cannot run securely.")

cipher = Fernet(ENCRYPTION_KEY.encode())

def encrypt_token(token: str) -> bytes:
    """Encrypts a string token."""
    return cipher.encrypt(token.encode('utf-8'))

def decrypt_token(encrypted_token: bytes) -> str:
    """Decrypts an encrypted token back to a string."""
    return cipher.decrypt(encrypted_token).decode('utf-8')