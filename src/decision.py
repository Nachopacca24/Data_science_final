"""La decisión: qué juegos comprar con un presupuesto fijo.

Combina las tres piezas del proyecto:
    calidad predicha (notebook 02)  x  parecido con los favoritos (notebook 03)  ->  puntaje
y elige la combinación de juegos con más puntaje total que cabe en el presupuesto.

Uso:
    from src.decision import tabla_candidatos, elegir_optimo
    cand = tabla_candidatos(favoritos=[379720, 1145360])
    lista = elegir_optimo(cand, presupuesto=300)
"""
import json
import math

import numpy as np
import pandas as pd

from src import config as C
from src.datos import cargar_juegos
from src.recomendador import similitud


def cargar_umbral() -> float:
    return json.loads((C.OUTPUTS / "umbral.json").read_text())["umbral"]


def tabla_candidatos(favoritos, descuento: float = C.DESCUENTO_TIPICO) -> pd.DataFrame:
    """Todos los juegos con su precio en oferta, calidad predicha, parecido y puntaje."""
    df = cargar_juegos()
    pred = pd.read_csv(C.OUTPUTS / "pred_calidad.csv")[["appid", "p_bien_recibido"]]
    sim = similitud(favoritos).rename("similitud").reset_index().rename(columns={"index": "appid"})

    t = (df[["appid", "nombre", "precio_lista_gtq", "es_gratis", "pct_positivo", "total_resenas", "bien_recibido"]]
         .merge(pred, on="appid").merge(sim, on="appid"))
    t["bien_recibido"] = t["bien_recibido"].astype(bool)
    t["precio_oferta_gtq"] = (t["precio_lista_gtq"] * (1 - descuento)).round(2)
    t["pasa_umbral"] = t["p_bien_recibido"] >= cargar_umbral()
    t["puntaje"] = t["p_bien_recibido"] * t["similitud"]
    return t


# El modelo propone, las reseñas reales confirman.
# El modelo estima la calidad SIN leer reseñas: sirve para juegos nuevos o con pocas reseñas.
# Cuando el juego ya tiene reseñas (todos los del dataset tienen >= C.MIN_RESENAS), se usan para
# confirmar: no se recomienda un juego que el modelo cree bueno pero las reseñas dicen que es malo,
# y no se manda a evitar uno que el modelo cree malo pero las reseñas dicen que es bueno.

def filtrar(cand: pd.DataFrame, n_candidatos: int = C.N_CANDIDATOS) -> pd.DataFrame:
    """Juegos de pago que pasan el umbral del modelo Y están bien reseñados de verdad;
    de esos, los más parecidos a los favoritos."""
    ok = cand[~cand["es_gratis"] & cand["pasa_umbral"] & cand["bien_recibido"]]
    return ok.nlargest(n_candidatos, "similitud")


def elegir_optimo(cand: pd.DataFrame, presupuesto: float = C.PRESUPUESTO_GTQ,
                  max_juegos: int = C.MAX_JUEGOS_LISTA) -> pd.DataFrame:
    """Problema de la mochila: maximiza la suma de puntajes sin pasarse del presupuesto
    ni de `max_juegos`. Programación dinámica sobre (juegos elegidos, quetzales gastados).

    Los precios se redondean hacia ARRIBA al quetzal, así que la lista nunca se pasa del
    presupuesto real (a cambio puede dejar sin usar algunos centavos)."""
    cand = cand.reset_index(drop=True)
    B = int(math.floor(presupuesto))
    costos = np.ceil(cand["precio_oferta_gtq"].to_numpy()).astype(int)
    valores = cand["puntaje"].to_numpy()

    # mejor[j, b] = mejor puntaje usando exactamente j juegos y gastando como máximo b quetzales
    mejor = np.full((max_juegos + 1, B + 1), -np.inf)
    mejor[0, :] = 0.0
    tomado = np.zeros((len(cand), max_juegos + 1, B + 1), dtype=bool)

    for i, (c, v) in enumerate(zip(costos, valores)):
        if c > B:
            continue
        for j in range(max_juegos, 0, -1):  # hacia atrás: cada juego se usa una sola vez
            nuevo = mejor[j - 1, : B + 1 - c] + v
            mejora = nuevo > mejor[j, c:]
            mejor[j, c:][mejora] = nuevo[mejora]
            tomado[i, j, c:] |= mejora
            tomado[i, j, c:][~mejora] = False

    # reconstruir la mejor combinación
    j, b = np.unravel_index(np.argmax(mejor), mejor.shape)
    elegidos = []
    for i in range(len(cand) - 1, -1, -1):
        if j > 0 and tomado[i, j, b]:
            elegidos.append(i)
            b -= costos[i]
            j -= 1
    return cand.loc[sorted(elegidos)].sort_values("puntaje", ascending=False).reset_index(drop=True)


def elegir_codicioso(cand: pd.DataFrame, presupuesto: float = C.PRESUPUESTO_GTQ,
                     max_juegos: int = C.MAX_JUEGOS_LISTA) -> pd.DataFrame:
    """Comparación simple: ordena por puntaje y va agregando mientras quepa."""
    elegidos, gastado = [], 0.0
    for _, fila in cand.sort_values("puntaje", ascending=False).iterrows():
        if len(elegidos) == max_juegos:
            break
        if gastado + fila["precio_oferta_gtq"] <= presupuesto:
            elegidos.append(fila)
            gastado += fila["precio_oferta_gtq"]
    return pd.DataFrame(elegidos).reset_index(drop=True)


def evitar(cand: pd.DataFrame, n: int = 5) -> pd.DataFrame:
    """Los juegos más tentadores (muy parecidos a los favoritos) que el modelo cree que NO serán
    bien recibidos Y cuyas reseñas reales lo confirman (no más de 80 % positivas)."""
    malos = cand[~cand["es_gratis"] & ~cand["pasa_umbral"] & ~cand["bien_recibido"]]
    return malos.nlargest(n, "similitud").reset_index(drop=True)
