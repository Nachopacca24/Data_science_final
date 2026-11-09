"""Límites del contrato y datos de la instancia (versión y ambiente).

Los límites son parte del contrato publicado en web/CONTRATO_API.md: si cambian aquí,
cambian allá y en las pruebas.
"""
import os
from pathlib import Path

WEB = Path(__file__).resolve().parents[1]
CATALOGO = WEB / "catalogo_demo.csv"
ESTATICOS = WEB / "pantallas"
ARCHIVO_VERSION = WEB / "VERSION"  # lo escribe el build con el SHA del commit

# --- Límites de entrada ---
PRESUPUESTO_MAX = 10_000  # quetzales
MAX_FAVORITOS = 5
MAX_JUEGOS_LISTA = 5      # igual que el notebook 05: la lista tiene como máximo 5 juegos
LIMITE_BUSQUEDA_DEFECTO = 20
LIMITE_BUSQUEDA_MAX = 1_000

AMBIENTES = {"dev", "prod"}


def version() -> str:
    """SHA del build. Orden: variable APP_VERSION, archivo web/VERSION, o 'local'."""
    if v := os.environ.get("APP_VERSION", "").strip():
        return v
    if ARCHIVO_VERSION.exists() and (v := ARCHIVO_VERSION.read_text().strip()):
        return v
    return "local"


def ambiente() -> str:
    """Ambiente de la instancia (APP_AMBIENTE). Un valor desconocido detiene el arranque."""
    a = os.environ.get("APP_AMBIENTE", "dev").strip().lower()
    if a not in AMBIENTES:
        raise ValueError(f"APP_AMBIENTE='{a}' no es válido; usa uno de {sorted(AMBIENTES)}")
    return a
