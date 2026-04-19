#!/usr/bin/env python3
#
import base64
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding


def desencolver_llave_fernet():
    try:
        # 1. LEER LA LLAVE PRIVADA DESDE EL ARCHIVO
        with open("privada.pem", "rb") as key_file:
            private_key = serialization.load_pem_private_key(
                key_file.read(), password=None
            )

        # 2. LEER EL TEXTO CIFRADO DESDE EL ARCHIVO token
        with open("token", "r") as f:
            llave_cifrada_b64 = f.read()

        # 3. DECODIFICAR BASE64 Y DESCIFRAR
        llave_cifrada_bytes = base64.b64decode(llave_cifrada_b64)

        llave_fernet = private_key.decrypt(
            llave_cifrada_bytes,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )

        print(f"[+] Llave Fernet recuperada: {llave_fernet.decode()}")
        return llave_fernet

    except Exception as e:
        print(f"[-] Error: {e}")


if __name__ == "__main__":
    desencolver_llave_fernet()
