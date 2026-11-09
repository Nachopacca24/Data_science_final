"""Carga web/catalogo_demo.csv una sola vez y lo deja en memoria."""
import csv
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from web.api import config

SEPARADOR_LISTA = "|"


@dataclass(frozen=True)
class Juego:
    appid: int
    nombre: str
    precio_gtq: float          # precio en oferta (precio de lista × (1 − descuento supuesto))
    etiquetas: tuple[str, ...]
    generos: tuple[str, ...]
    p_bien_recibido: float     # probabilidad que da el modelo del notebook 02
    pasa_umbral: bool          # p_bien_recibido ≥ umbral elegido por costos
    pct_positivo: float        # % real de reseñas positivas
    imagen: str

    @property
    def es_gratis(self) -> bool:
        return self.precio_gtq == 0

    @property
    def precio_centavos(self) -> int:
        return round(self.precio_gtq * 100)


def _lista(celda: str) -> tuple[str, ...]:
    return tuple(x for x in celda.split(SEPARADOR_LISTA) if x)


def _booleano(celda: str) -> bool:
    if celda not in {"True", "False"}:
        raise ValueError(f"se esperaba True o False y llegó '{celda}'")
    return celda == "True"


def leer(ruta: Path) -> dict[int, Juego]:
    """Lee el CSV y valida cada fila. Un catálogo dañado detiene el arranque de la API."""
    juegos: dict[int, Juego] = {}
    with ruta.open(encoding="utf-8", newline="") as f:
        for n, fila in enumerate(csv.DictReader(f), start=2):  # la fila 1 es el encabezado
            try:
                j = Juego(
                    appid=int(fila["appid"]),
                    nombre=fila["nombre"],
                    precio_gtq=float(fila["precio_gtq"]),
                    etiquetas=_lista(fila["etiquetas"]),
                    generos=_lista(fila["generos"]),
                    p_bien_recibido=float(fila["p_bien_recibido"]),
                    pasa_umbral=_booleano(fila["pasa_umbral"]),
                    pct_positivo=float(fila["pct_positivo"]),
                    imagen=fila["imagen"],
                )
            except (KeyError, ValueError) as e:
                raise ValueError(f"{ruta.name}, fila {n}: {e}") from e
            if j.appid <= 0 or j.precio_gtq < 0 or not 0 <= j.p_bien_recibido <= 1:
                raise ValueError(f"{ruta.name}, fila {n}: valores fuera de rango")
            if j.appid in juegos:
                raise ValueError(f"{ruta.name}, fila {n}: appid {j.appid} repetido")
            juegos[j.appid] = j
    if not juegos:
        raise ValueError(f"{ruta.name} está vacío")
    return juegos


@lru_cache(maxsize=1)
def catalogo() -> dict[int, Juego]:
    return leer(config.CATALOGO)
