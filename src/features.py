"""Construcción de la matriz de predictores para el clasificador de calidad.

Solo usa información que existe al publicar el juego (nada de reseñas, owners ni playtime).
"""
import numpy as np
import pandas as pd

from src import config as C

NUMERICAS = ["log_precio", "antiguedad_anios", "n_idiomas", "log_logros", "log_dlc", "edad_requerida"]
BINARIAS = ["es_gratis", "windows", "mac", "linux"]
CATEGORICAS = ["desarrollador", "publicador"]  # alta cardinalidad -> TargetEncoder dentro del Pipeline


def _multi_hot(serie: pd.Series, prefijo: str, min_juegos: int) -> pd.DataFrame:
    """Una columna 0/1 por valor de la lista que aparece en al menos `min_juegos` juegos.
    El vocabulario se elige por frecuencia (no mira el objetivo), así que no filtra información."""
    largo = serie.map(list).explode()
    conteo = largo.value_counts()
    vocab = conteo[conteo >= min_juegos].index
    largo = largo[largo.isin(vocab)]
    dummies = pd.crosstab(largo.index, largo).reindex(serie.index, fill_value=0)
    dummies = dummies.reindex(columns=vocab, fill_value=0).clip(upper=1).astype(np.uint8)
    dummies.columns = [f"{prefijo}_{c}" for c in dummies.columns]
    return dummies


def construir_X(df: pd.DataFrame, min_juegos_etiqueta: int = 300) -> pd.DataFrame:
    X = pd.DataFrame(index=df.index)
    X["log_precio"] = np.log1p(df["precio_lista_usd"])
    X["antiguedad_anios"] = df["antiguedad_anios"]
    X["n_idiomas"] = df["n_idiomas"]
    X["log_logros"] = np.log1p(df["logros"])
    X["log_dlc"] = np.log1p(df["dlc_count"])
    X["edad_requerida"] = df["edad_requerida"]
    for b in BINARIAS:
        X[b] = df[b].astype(np.uint8)
    X["desarrollador"] = df["desarrolladores"].map(lambda l: l[0] if len(l) else "desconocido")
    X["publicador"] = df["publicadores"].map(lambda l: l[0] if len(l) else "desconocido")

    partes = [
        X,
        _multi_hot(df["generos"], "gen", 100),
        _multi_hot(df["categorias"], "cat", 300),
        _multi_hot(df["etiquetas"], "tag", min_juegos_etiqueta),
    ]
    X = pd.concat(partes, axis=1)
    assert not set(X.columns) & set(C.COLUMNAS_PROHIBIDAS), "columna prohibida en X"
    return X
