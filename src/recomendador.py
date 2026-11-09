"""Recomendador por parecido de etiquetas y géneros (similitud coseno).

Uso desde un notebook:
    from src.recomendador import recomendar, similitud
    recomendar([379720], k=10)          # "si te gustó DOOM..."
    recomendar(["DOOM", "Hades"], k=10)  # también acepta nombres
    similitud([379720])                  # parecido de TODOS los juegos, para el 05
"""
from functools import lru_cache

import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

from src import config as C
from src.datos import cargar_juegos
from src.features import _multi_hot


@lru_cache(maxsize=1)
def matriz_gustos():
    """Devuelve (juegos, matriz). Cada fila de la matriz es un juego: 1 si tiene esa
    etiqueta o género, 0 si no. Se calcula una vez y queda guardada."""
    df = cargar_juegos()
    M = pd.concat([
        _multi_hot(df["generos"], "gen", C.MIN_JUEGOS_ETIQUETA),
        _multi_hot(df["etiquetas"], "tag", C.MIN_JUEGOS_ETIQUETA),
    ], axis=1)
    M.index = df["appid"].values
    return df.set_index("appid"), M


def _a_appids(favoritos, juegos: pd.DataFrame) -> list[int]:
    """Acepta appids o nombres. Si un nombre se repite, toma el juego con más reseñas."""
    appids = []
    for f in favoritos:
        if isinstance(f, (int, np.integer)):
            if f not in juegos.index:
                raise ValueError(f"appid {f} no está en el dataset")
            appids.append(int(f))
            continue
        hits = juegos[juegos["nombre"].str.lower() == str(f).lower()]
        if hits.empty:
            raise ValueError(f"no encontré el juego '{f}'; usa su appid")
        appids.append(int(hits["total_resenas"].idxmax()))
    return appids


def similitud(favoritos) -> pd.Series:
    """Parecido (0 a 1) de cada juego con el perfil promedio de los favoritos.
    Índice: appid. Los favoritos quedan fuera."""
    juegos, M = matriz_gustos()
    ids = _a_appids(favoritos, juegos)
    perfil = M.loc[ids].mean(axis=0).to_numpy().reshape(1, -1)
    s = pd.Series(cosine_similarity(perfil, M.to_numpy())[0], index=M.index, name="similitud")
    s = s.rename_axis("appid")  # para poder unirla por appid en el 05
    return s.drop(ids)


def recomendar(favoritos, k: int = 10) -> pd.DataFrame:
    """Los k juegos más parecidos a los favoritos: appid, nombre, similitud."""
    juegos, _ = matriz_gustos()
    top = similitud(favoritos).nlargest(k)

    tabla = pd.DataFrame({
        "appid": top.index,
        "nombre": juegos.loc[top.index, "nombre"].values,
        "similitud": top.round(3).values,
    })
    return tabla
