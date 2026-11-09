"""Genera web/catalogo_demo.csv: el catálogo pequeño que usa la API.

La API no carga el dataset completo (400 MB). Usa una muestra fija que se sube a git:
los N juegos con más reseñas en los que el modelo y las reseñas reales están de acuerdo
("el modelo propone, las reseñas confirman", igual que el notebook 05). Así, dentro del
catálogo, `pasa_umbral` ya es la regla completa para recomendar un juego.

Uso desde la raíz del repo (necesita el dataset y outputs/pred_calidad.csv del notebook 02):
    python -m web.construir_catalogo
"""
import json

import pandas as pd

from src import config as C
from src.datos import cargar_juegos

N_JUEGOS = 500
SEPARADOR_LISTA = "|"  # etiquetas y géneros van en una sola celda: "Action|FPS|Shooter"
DESTINO = C.RAIZ / "web" / "catalogo_demo.csv"
COLUMNAS = ["appid", "nombre", "precio_gtq", "etiquetas", "generos",
            "p_bien_recibido", "pasa_umbral", "pct_positivo", "imagen"]


def construir() -> pd.DataFrame:
    umbral = json.loads((C.OUTPUTS / "umbral.json").read_text())["umbral"]
    pred = pd.read_csv(C.OUTPUTS / "pred_calidad.csv")[["appid", "p_bien_recibido"]]
    t = cargar_juegos().merge(pred, on="appid")

    t["pasa_umbral"] = t["p_bien_recibido"] >= umbral
    t = t[t["pasa_umbral"] == t["bien_recibido"].astype(bool)]  # modelo y reseñas de acuerdo
    t = t.nlargest(N_JUEGOS, "total_resenas")

    t["precio_gtq"] = t["precio_oferta_gtq"]
    for col in ["etiquetas", "generos"]:
        t[col] = t[col].map(lambda xs: SEPARADOR_LISTA.join(x.replace(SEPARADOR_LISTA, "/") for x in xs))
    t["p_bien_recibido"] = t["p_bien_recibido"].round(4)
    t["pct_positivo"] = t["pct_positivo"].round(4)
    return t[COLUMNAS].sort_values("appid").reset_index(drop=True)


if __name__ == "__main__":
    cat = construir()
    cat.to_csv(DESTINO, index=False)
    print(f"{len(cat)} juegos -> {DESTINO} ({cat['pasa_umbral'].sum()} pasan el umbral)")
