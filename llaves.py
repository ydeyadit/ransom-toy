#!/usr/bin/env python3
# PARA GENERAR LLAVES RSA
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

# PRIVADA
privada = rsa.generate_private_key(public_exponent=65537, key_size=2048)
with open("privada.pem", "wb") as f:
    f.write(
        privada.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )
    )
# PUBLICA
publica = privada.public_key()
with open("publica.pem", "wb") as f:
    f.write(
        publica.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
    )
