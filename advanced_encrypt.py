import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

from cryptography.hazmat.primitives import padding

backend = default_backend()
key = os.urandom(16) # size 32 for aes-256, size 16 for aes-128
iv = os.urandom(16)

cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=backend)
encryptor = cipher.encryptor()
padder = padding.PKCS7(128).padder()

padded_data = padder.update(b"a bigger secret message") + padder.finalize()

ct = encryptor.update(padded_data) + encryptor.finalize()

decryptor = cipher.decryptor()
decrypted_data = decryptor.update(ct) + decryptor.finalize()
print(decrypted_data)

unpadder = padding.PKCS7(128).unpadder()
data = unpadder.update(decrypted_data) + unpadder.finalize()
print(data)
