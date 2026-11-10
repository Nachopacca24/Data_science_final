"""Verifica que una instancia desplegada esté viva y sea la versión correcta.

1. Espera a que GET /salud responda {"estado": "ok"} (hasta --espera segundos).
2. Revisa que GET /version diga exactamente el SHA y el ambiente esperados.

Si algo no cuadra, termina con código 1 y el pipeline se detiene: así nunca se prueba
(ni se da por buena) una versión distinta a la que se construyó.

Uso:
    python ci/verificar_despliegue.py --url http://localhost:8001 --sha <sha> --ambiente dev
Solo usa la librería estándar.
"""
import argparse
import json
import sys
import time
import urllib.error
import urllib.request


def obtener(url: str, timeout: float = 3) -> dict:
    with urllib.request.urlopen(url, timeout=timeout) as r:
        return json.load(r)


def esperar_salud(url: str, espera: float, intervalo: float = 1) -> None:
    limite = time.monotonic() + espera
    ultimo_error = None
    while time.monotonic() < limite:
        try:
            if obtener(f"{url}/salud").get("estado") == "ok":
                return
            ultimo_error = "respondió, pero el estado no es 'ok'"
        except (urllib.error.URLError, ConnectionError, TimeoutError, json.JSONDecodeError) as e:
            ultimo_error = e
        time.sleep(intervalo)
    raise SystemExit(f"FALLA: {url}/salud no respondió 'ok' en {espera:.0f} s (último error: {ultimo_error})")


def verificar_version(url: str, sha: str, ambiente: str) -> dict:
    v = obtener(f"{url}/version")
    problemas = []
    if v.get("version") != sha:
        problemas.append(f"version es '{v.get('version')}' y se esperaba '{sha}'")
    if v.get("ambiente") != ambiente:
        problemas.append(f"ambiente es '{v.get('ambiente')}' y se esperaba '{ambiente}'")
    if problemas:
        raise SystemExit("FALLA: " + "; ".join(problemas))
    return v


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--url", required=True)
    p.add_argument("--sha", required=True)
    p.add_argument("--ambiente", required=True, choices=["dev", "prod"])
    p.add_argument("--espera", type=float, default=60, help="segundos máximos esperando /salud")
    a = p.parse_args(argv)
    url = a.url.rstrip("/")

    esperar_salud(url, a.espera)
    v = verificar_version(url, a.sha, a.ambiente)
    print(f"OK: {url} responde version={v['version']} ambiente={v['ambiente']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
