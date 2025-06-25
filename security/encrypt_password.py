#!/usr/bin/env python3
"""
AES-128-CBC password encryption for dbxplorer agent inventory files.
Usage:
  export DB_PASSWORD_KEY='your16charsecret'
  python encrypt_password.py 'my_db_password'
Output:
  enc[<base64-iv>:<base64-ciphertext>]
"""
import os
import sys
import base64
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

def pad(s):
    pad_len = 16 - (len(s) % 16)
    return s + bytes([pad_len] * pad_len)

def main():
    if len(sys.argv) != 2:
        print("Usage: python encrypt_password.py <password>")
        sys.exit(1)
    password = sys.argv[1].encode()
    key = os.environ.get('DB_PASSWORD_KEY')
    if not key or len(key) != 16:
        print("Error: DB_PASSWORD_KEY env var must be set to 16 characters (128 bits)")
        sys.exit(2)
    key_bytes = key.encode()
    iv = get_random_bytes(16)
    cipher = AES.new(key_bytes, AES.MODE_CBC, iv)
    ciphertext = cipher.encrypt(pad(password))
    print(f"enc[{base64.b64encode(iv).decode()}:{base64.b64encode(ciphertext).decode()}]")

if __name__ == "__main__":
    main() 
