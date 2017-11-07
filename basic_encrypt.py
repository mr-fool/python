import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

backend = default_backend()
key = os.urandom(32) # size 32 for aes-256, size 16 for aes-128
iv = os.urandom(16)

cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=backend)

encryptor = cipher.encryptor()
ct = encryptor.update(b"a secret message") + encryptor.finalize()
#ct = encryptor.update(b"a bigger secret message") + encryptor.finalize()

decryptor = cipher.decryptor()
print( decryptor.update(ct) + decryptor.finalize() )
