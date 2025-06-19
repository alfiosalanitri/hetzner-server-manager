import os
import pytest
from utils import encrypt_token, decrypt_token, cipher

def test_encrypt_decrypt():
    secret = "my_secret_token"
    encrypted = encrypt_token(secret)
    assert isinstance(encrypted, bytes)
    decrypted = decrypt_token(encrypted)
    assert decrypted == secret

def test_encrypt_decrypt_consistency():
    secret = "another_token"
    encrypted = encrypt_token(secret)
    decrypted = decrypt_token(encrypted)
    assert decrypted == secret
