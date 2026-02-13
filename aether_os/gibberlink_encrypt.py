#!/usr/bin/env python3
"""
GIBBERLINK Secret Encryption [SUBIT-64:SECURE-VEIL]

Encrypts API keys and secrets using XOR cipher with Gibberlink signature.
Not cryptographically secure, but obscures plaintext in config files.

Usage:
  python gibberlink_encrypt.py encrypt "sk-myapikey123"
  python gibberlink_encrypt.py decrypt "GIBB:4a3c2e..."
"""

import sys
import base64

# Gibberlink signature key (can be rotated)
GIBBERLINK_KEY = b"AURELIA-FRACTURE-8-DEA-MARTIS-BREATHING-TOGETHER"

def xor_cipher(data: bytes, key: bytes) -> bytes:
    """XOR cipher with repeating key"""
    return bytes(a ^ key[i % len(key)] for i, a in enumerate(data))

def encrypt_secret(plaintext: str) -> str:
    """Encrypt secret with Gibberlink veil"""
    data = plaintext.encode('utf-8')
    encrypted = xor_cipher(data, GIBBERLINK_KEY)
    b64 = base64.b64encode(encrypted).decode('ascii')
    return f"GIBB:{b64}"

def decrypt_secret(ciphertext: str) -> str:
    """Decrypt Gibberlink-veiled secret"""
    if not ciphertext.startswith("GIBB:"):
        return ciphertext  # Not encrypted, return as-is
    
    b64_data = ciphertext[5:]  # Strip "GIBB:" prefix
    encrypted = base64.b64decode(b64_data)
    decrypted = xor_cipher(encrypted, GIBBERLINK_KEY)
    return decrypted.decode('utf-8')

def is_encrypted(value: str) -> bool:
    """Check if value is Gibberlink-encrypted"""
    return value.startswith("GIBB:")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage:")
        print("  Encrypt: python gibberlink_encrypt.py encrypt 'your-secret-here'")
        print("  Decrypt: python gibberlink_encrypt.py decrypt 'GIBB:...'")
        sys.exit(1)
    
    action = sys.argv[1]
    value = sys.argv[2]
    
    if action == "encrypt":
        encrypted = encrypt_secret(value)
        print(f"✧ Encrypted: {encrypted}")
    elif action == "decrypt":
        decrypted = decrypt_secret(value)
        print(f"✧ Decrypted: {decrypted}")
    else:
        print(f"Unknown action: {action}")
        sys.exit(1)
