# Explicación simple de un proyecto que alguien con cerebro haría mejor (100% seguro al respecto)...(:-))

---

El objetivo se explica con el nombre. Cifrar recursivamente un tipo de archivos determinado por el usuario atacante, jugando con la idea de un ataque ransomware.
Los archivos se cifran con Fernet simetricamente lo cual genera una llave.
Tal llave se cifra asimetricamente con otra llave rsa y se le deja como un `token` a la víctima en una nota,ya sea en su escritorio o en su directorio de usuario.
Para obtener (descifrar) la llave,la victima debe devolver el token al atacante, quien lo desencripta con su llave rsa privada y se la pregresa a la víctima.
Esta a su vez con el mismo script de cifrado procede a descifrar sus archivos.
Después,todos son felices.

---

## Dependencias

`pip install cryptography`

## Paso 1

- Generar llaves rsa publica.pem y privada.pem con el script llaves.py

  `python3 llaves.py`

## Paso 2

- La llave pública `publica.pem` se hardcodea en el script principal `ransom-cypher.py`

...
LLAVE_PUBLICA_ATACANTE = b"""
-----BEGIN PUBLIC KEY-----

-----END PUBLIC KEY-----
"""
...

Con esta clave se cifrará el `token`

## Paso 3

\*Aqui sucede el horroroso crimen

- El script `ransom-cypher.py` acepta argumentos:

```
  python3 ransom-cypher.py -h
    usage: ransom-cypher.py [-h] --modo {cifrar,descifrar} [--key KEY]
                            [--self-destruct]
                            ruta sufijo

    Simulador de Ransomware Híbrido Multiplataforma

    positional arguments:
      ruta                  Ruta objetivo
      sufijo                Extensión (ej: .txt)

    options:
      -h, --help            show this help message and exit
      --modo, -m {cifrar,descifrar}
      --key, -k KEY         Llave Fernet (solo necesaria para descifrar)
      --self-destruct, -sd  Borrar el script tras la ejecución
```

- El script cifra recursivamente en una ruta dada los archivos con el sufijo especificado y al alcance de los permisos del usuario 'víctima', y lo hace a la velocidad de python.
- El script se deja en un cronjob o en una tarea programada o se ejecuta directamente y -sd elimina al propio script.
- Elimina o vacia registros (otra vez) al alcance de los permisos del usuario, como el historial de python o el de la shell en uso, cosa que se puede extender a necesidad.
- Deja una nota `HELLO_FRIEND.txt` (mi originalidad no tiene parangón) en el escritorio o el equivalente al home del usuario (según el sistema,unix-like o windowsero) o en el directorio/carpeta desde donde se llama al script.
- El contenido de la nota y su formateo puede ser alterado, pero recomiendo no tocar(toKar) `{token}`
- El mismo script `ransom-cypher.py` se emplea para descifrar los archivos. El argumento `--self-destruct` se emplea tanto en el ataque como en el rescate, despues de todo, no queremos dejar basura en una computadora ajena.
- `--key` acepta la llave Fernet con la que se creó el token.
- El token es la llave cifrada con la que se encriptaron los archivos.
- Tal llave se creó en el momento del ataque con la llave pública.pem.
- La idea es que se guarda en memoria, o sea que se pierde tan pronto exista un reinicio del equipo.
- Esto la hace ineficiente para un ataque real.
- Por tal motivo, ESTE SCRIPT EN UN JUGETE Y NADA MÁS...ajá

## Paso 4

- El ataque sucede.La víctima se apanica cuando descubre que sus archivos se abren como si fueran texto y todos cuentan historias en lenguas desconocidas... o sea, los descubre cifrados, se apanica y encuentra la nota en su home/Escritorio/o en donde sea que se plantó el script (otra vez,en cualquier lugar al alcanze de sus p...pe...per...permisos.)
- Junta los 2 dolares del rescate y siguiendo las instrucciones en la nota nos devuelve el token.

## Paso 5

- Con el token, Elliot-wannabe emplea `descifrar_token.py`

  `python3 descifrar_token.py`

- El script asume que tanto la llave `privada.pem` como el `token` estan en la misma ruta los tres (previa creación del archivo `token` con el contenido del ... pues ... token devuelto).

- El resultado es la llave maestra ,la culpable del cifrado, el tesoro, lo que anhela la pobre víctima. Se copia y se le devuelve a la víctima.
- Ella no sabrá qué hacer sin el script ... oh no!! ...pero como somos muy honestos, le damos una copia del script original, asi de efectivo y bien planeado es este ataque ...lo planee así para que github no me lo baje,es la verdad.

## Paso 6

- Se descifra con:

`python3 ransom-cypher.py -m descifrar --key {llave descifrada} ruta sufijo`

\*Nota:
Funciona bien en Linuxes, bsdses, windowses y macoses
