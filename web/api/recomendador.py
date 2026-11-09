"""La decisión del notebook 05, en versión liviana para la API (sin pandas ni sklearn).

    puntaje = calidad predicha × parecido con los favoritos
    lista   = la combinación de hasta 5 juegos con más puntaje total que cabe en el presupuesto

Un juego es candidato si: pasa el umbral de calidad, es de pago y no es uno de los favoritos.
"""
import math
from collections import Counter
from dataclasses import dataclass

from web.api.catalogo import Juego


def _rasgos(j: Juego) -> set[str]:
    """Etiquetas y géneros del juego. Llevan prefijo porque hay nombres repetidos ("Action")."""
    return {f"tag:{t}" for t in j.etiquetas} | {f"gen:{g}" for g in j.generos}


def similitud(favoritos: list[Juego], juego: Juego) -> float:
    """Similitud coseno entre el juego (vector de 0/1) y el perfil promedio de los favoritos."""
    perfil = Counter()
    for f in favoritos:
        perfil.update(_rasgos(f))
    rasgos = _rasgos(juego)
    if not perfil or not rasgos:
        return 0.0
    n = len(favoritos)
    producto = sum(perfil[r] for r in rasgos) / n
    norma_perfil = math.sqrt(sum((c / n) ** 2 for c in perfil.values()))
    return producto / (norma_perfil * math.sqrt(len(rasgos)))


@dataclass(frozen=True)
class Candidato:
    juego: Juego
    similitud: float

    @property
    def puntaje(self) -> float:
        return self.juego.p_bien_recibido * self.similitud


def candidatos(catalogo: dict[int, Juego], favoritos: list[Juego]) -> list[Candidato]:
    ids_favoritos = {f.appid for f in favoritos}
    return [
        Candidato(j, similitud(favoritos, j))
        for j in sorted(catalogo.values(), key=lambda j: j.appid)  # orden fijo = resultado repetible
        if j.pasa_umbral and not j.es_gratis and j.appid not in ids_favoritos
    ]


def elegir(cands: list[Candidato], presupuesto_centavos: int, max_juegos: int) -> list[Candidato]:
    """Mochila exacta: maximiza la suma de puntajes sin pasarse del presupuesto ni de max_juegos.

    Se trabaja en centavos (enteros), así que "cuesta justo lo que tengo" sí cabe.
    Para cada cantidad de juegos k se guardan solo los estados que valen la pena
    (frontera de Pareto: nadie más barato con igual o más puntaje).
    A igual puntaje se prefiere la lista con más juegos y después la más barata.
    """
    # estados[k] = lista de (costo, puntaje, índices elegidos)
    estados: list[list[tuple[int, float, tuple[int, ...]]]] = [[(0, 0.0, ())]] + [[] for _ in range(max_juegos)]

    for i, c in enumerate(cands):
        costo = c.juego.precio_centavos
        if costo > presupuesto_centavos:
            continue
        for k in range(max_juegos, 0, -1):  # hacia atrás: cada juego se usa una sola vez
            nuevos = [(g + costo, p + c.puntaje, idx + (i,))
                      for g, p, idx in estados[k - 1] if g + costo <= presupuesto_centavos]
            if nuevos:
                estados[k] = _frontera(estados[k] + nuevos)

    mejor = max(
        ((g, p, idx) for nivel in estados for g, p, idx in nivel),
        key=lambda e: (round(e[1], 9), len(e[2]), -e[0]),
    )
    return sorted((cands[i] for i in mejor[2]), key=lambda c: (-c.puntaje, c.juego.appid))


def _frontera(estados):
    """Del más barato al más caro, conserva solo los que suben el puntaje."""
    estados.sort(key=lambda e: (e[0], -e[1]))
    frontera, mejor = [], -math.inf
    for e in estados:
        if e[1] > mejor:
            frontera.append(e)
            mejor = e[1]
    return frontera
