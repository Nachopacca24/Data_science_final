"""Configuración compartida de las pruebas de integración (caja negra contra la API desplegada).

Variables de entorno:
    API_URL   URL de la instancia a probar (por defecto http://localhost:8000)

Suites:
    pytest tests/integracion -m smoke   -> solo lo básico
    pytest tests/integracion            -> regresión completa
"""
import os

import pytest
import requests

API_URL = os.environ.get("API_URL", "http://localhost:8000").rstrip("/")
TIEMPO_MAXIMO = 10  # segundos por petición

# --- Contrato provisional: ajustar cuando D publique el formato oficial ---
PRESUPUESTO_MAX = float(os.environ.get("PRESUPUESTO_MAX", 10_000))
MAX_FAVORITOS = int(os.environ.get("MAX_FAVORITOS", 5))
APPID_INEXISTENTE = 999_999_999


def pytest_configure(config):
    config.addinivalue_line("markers", "smoke: casos mínimos para saber si la API está viva")


@pytest.fixture(scope="session")
def api():
    """Cliente HTTP con la URL base ya puesta. Falla de inmediato si la API no responde."""
    sesion = requests.Session()

    class Cliente:
        url = API_URL

        def get(self, ruta, **kw):
            return sesion.get(f"{API_URL}{ruta}", timeout=TIEMPO_MAXIMO, **kw)

        def post(self, ruta, **kw):
            return sesion.post(f"{API_URL}{ruta}", timeout=TIEMPO_MAXIMO, **kw)

    cliente = Cliente()
    try:
        cliente.get("/salud")
    except requests.ConnectionError:
        pytest.exit(f"La API no responde en {API_URL}", returncode=1)
    print(f"\nProbando contra: {API_URL}")
    return cliente


@pytest.fixture(scope="session")
def catalogo(api):
    """Juegos de referencia tomados de la propia API, para no depender del código.
    TODO: cuando exista web/catalogo_demo.csv, fijar aquí appids conocidos de ese archivo."""
    r = api.get("/juegos", params={"buscar": "", "limite": 1000})
    r.raise_for_status()
    return r.json()


@pytest.fixture(scope="session")
def un_appid(catalogo):
    return catalogo[0]["appid"]


@pytest.fixture
def cuerpo_valido(un_appid):
    """Una petición válida de recomendaciones. Cada caso cambia solo el campo que prueba."""
    return {"presupuesto": 300, "favoritos": [un_appid]}
