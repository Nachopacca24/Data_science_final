"""Configuración de las pruebas end-to-end (Playwright + pytest).

- La URL sale de BASE_URL: el pipeline la apunta a la instancia desplegada (dev o prod).
- El navegador lo elige el pipeline con --browser (parámetro `navegador`).
- El marcador `smoke` se registra aquí para no tocar pyproject.toml, que es compartido.
"""
import os

import pytest

from paginas.busqueda_pagina import BusquedaPagina
from paginas.resultados_pagina import ResultadosPagina


def pytest_configure(config):
    config.addinivalue_line("markers", "smoke: recorrido mínimo que siempre debe pasar")


@pytest.fixture(scope="session")
def base_url():
    return os.environ.get("BASE_URL", "http://localhost:8000")


@pytest.fixture
def busqueda(page):
    return BusquedaPagina(page).abrir()


@pytest.fixture
def resultados(page):
    return ResultadosPagina(page)
