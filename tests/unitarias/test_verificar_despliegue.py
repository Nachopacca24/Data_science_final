"""Pruebas unitarias del script que verifica cada despliegue (ci/verificar_despliegue.py)."""
import importlib.util
from pathlib import Path

import pytest

RUTA = Path(__file__).resolve().parents[2] / "ci" / "verificar_despliegue.py"
spec = importlib.util.spec_from_file_location("verificar_despliegue", RUTA)
vd = importlib.util.module_from_spec(spec)
spec.loader.exec_module(vd)

SHA = "945e292"


@pytest.fixture
def instancia(monkeypatch):
    """Simula la API: cada prueba define qué responde /salud y /version."""
    respuestas = {"/salud": {"estado": "ok"}, "/version": {"version": SHA, "ambiente": "dev"}}

    def obtener(url, timeout=3):
        ruta = url.removeprefix("http://api")
        r = respuestas[ruta]
        if isinstance(r, Exception):
            raise r
        return r

    monkeypatch.setattr(vd, "obtener", obtener)
    return respuestas


def test_version_y_ambiente_correctos(instancia):
    assert vd.main(["--url", "http://api/", "--sha", SHA, "--ambiente", "dev", "--espera", "1"]) == 0


def test_sha_distinto_detiene_el_pipeline(instancia):
    instancia["/version"] = {"version": "otro-sha", "ambiente": "dev"}
    with pytest.raises(SystemExit, match="version es 'otro-sha'"):
        vd.main(["--url", "http://api", "--sha", SHA, "--ambiente", "dev", "--espera", "1"])


def test_ambiente_distinto_detiene_el_pipeline(instancia):
    with pytest.raises(SystemExit, match="ambiente es 'dev'"):
        vd.main(["--url", "http://api", "--sha", SHA, "--ambiente", "prod", "--espera", "1"])


def test_api_que_no_responde_agota_la_espera(instancia):
    instancia["/salud"] = ConnectionError("conexión rechazada")
    with pytest.raises(SystemExit, match="no respondió 'ok'"):
        vd.esperar_salud("http://api", espera=0.3, intervalo=0.1)


def test_ambiente_desconocido_es_error_de_uso(instancia):
    with pytest.raises(SystemExit):
        vd.main(["--url", "http://api", "--sha", SHA, "--ambiente", "qa"])
