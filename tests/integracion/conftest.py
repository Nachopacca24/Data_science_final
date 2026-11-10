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

# --- Límites del contrato oficial (web/CONTRATO_API.md) ---
# Se copian aquí a propósito, sin importar web/: son pruebas de caja negra y no leen el código.
PRESUPUESTO_MAX = float(os.environ.get("PRESUPUESTO_MAX", 10_000))
MAX_FAVORITOS = int(os.environ.get("MAX_FAVORITOS", 5))
MAX_JUEGOS_LISTA = 5
LIMITE_BUSQUEDA_MAX = 1_000
MAX_BUSCAR = 100            # caracteres del texto de búsqueda
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
    """Juegos de referencia tomados de la propia API (no del CSV), para no depender del código ni
    de qué juegos tenga el catálogo: si el catálogo cambia, las pruebas siguen sirviendo."""
    r = api.get("/juegos", params={"buscar": "", "limite": LIMITE_BUSQUEDA_MAX})
    r.raise_for_status()
    return r.json()


@pytest.fixture(scope="session")
def un_appid(catalogo):
    return catalogo[0]["appid"]


@pytest.fixture
def cuerpo_valido(un_appid):
    """Una petición válida de recomendaciones. Cada caso cambia solo el campo que prueba."""
    return {"presupuesto": 300, "favoritos": [un_appid]}
