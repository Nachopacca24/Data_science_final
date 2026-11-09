"""Pruebas unitarias de la lógica de recomendación con un catálogo chico hecho a mano."""
import itertools

import pytest

from web.api.catalogo import Juego
from web.api.recomendador import Candidato, candidatos, elegir, similitud


def juego(appid, precio=10.0, etiquetas=("Action",), p=0.9, pasa=True, generos=()):
    return Juego(appid=appid, nombre=f"Juego {appid}", precio_gtq=precio, etiquetas=tuple(etiquetas),
                 generos=tuple(generos), p_bien_recibido=p, pasa_umbral=pasa, pct_positivo=0.9, imagen="")


def cand(appid, precio, puntaje):
    """Candidato con el puntaje exacto que se quiere (similitud = 1, calidad = puntaje)."""
    return Candidato(juego(appid, precio=precio, p=puntaje), similitud=1.0)


def centavos(q):
    return round(q * 100)


# ---------- similitud ----------

def test_similitud_identica_es_uno():
    a = juego(1, etiquetas=("FPS", "Action"))
    assert similitud([a], juego(2, etiquetas=("FPS", "Action"))) == pytest.approx(1.0)


def test_similitud_sin_nada_en_comun_es_cero():
    assert similitud([juego(1, etiquetas=("FPS",))], juego(2, etiquetas=("Puzzle",))) == 0


def test_similitud_sin_etiquetas_es_cero():
    assert similitud([juego(1, etiquetas=("FPS",))], juego(2, etiquetas=())) == 0


def test_similitud_crece_con_lo_que_comparten():
    fav = juego(1, etiquetas=("FPS", "Action", "Gore"))
    poco = similitud([fav], juego(2, etiquetas=("FPS", "Puzzle", "Cute")))
    mucho = similitud([fav], juego(3, etiquetas=("FPS", "Action", "Cute")))
    assert 0 < poco < mucho < 1


def test_etiqueta_y_genero_con_el_mismo_nombre_no_se_confunden():
    fav = juego(1, etiquetas=("Action",), generos=())
    assert similitud([fav], juego(2, etiquetas=(), generos=("Action",))) == 0


# ---------- candidatos (tabla de decisión: ¿puede entrar?) ----------

def test_candidatos_aplica_las_tres_reglas():
    fav = juego(1)
    cat = {j.appid: j for j in [
        fav,                         # es favorito -> fuera
        juego(2, pasa=False),        # no pasa el umbral -> fuera
        juego(3, precio=0),          # gratis: no hay nada que comprar -> fuera
        juego(4),                    # pasa, de pago, no favorito -> candidato
    ]}
    assert [c.juego.appid for c in candidatos(cat, [fav])] == [4]


def test_puntaje_es_calidad_por_parecido():
    c = Candidato(juego(1, p=0.8), similitud=0.5)
    assert c.puntaje == pytest.approx(0.4)


# ---------- mochila ----------

def test_elige_la_mejor_combinacion_no_la_codiciosa():
    # Codicioso tomaría A (el de más puntaje) y ya no cabe nada: 0.9.
    # Lo óptimo es B + C: 0.6 + 0.6 = 1.2.
    cands = [cand(1, 100, 0.9), cand(2, 50, 0.6), cand(3, 50, 0.6)]
    assert {c.juego.appid for c in elegir(cands, centavos(100), 5)} == {2, 3}


def test_precio_igual_al_presupuesto_cabe():
    assert [c.juego.appid for c in elegir([cand(1, 38.30, 0.5)], centavos(38.30), 5)] == [1]


def test_un_centavo_menos_ya_no_cabe():
    assert elegir([cand(1, 38.30, 0.5)], centavos(38.29), 5) == []


def test_respeta_el_maximo_de_juegos():
    cands = [cand(i, 1, 0.5) for i in range(1, 11)]
    assert len(elegir(cands, centavos(1000), 5)) == 5


def test_sin_candidatos_devuelve_lista_vacia():
    assert elegir([], centavos(300), 5) == []


def test_a_igual_puntaje_prefiere_mas_juegos():
    # Un juego sin parecido (puntaje 0) que cabe sí se recomienda: mejor que una lista vacía.
    assert len(elegir([cand(1, 10, 0.0)], centavos(10), 5)) == 1


def test_resultado_ordenado_por_puntaje():
    cands = [cand(1, 10, 0.2), cand(2, 10, 0.9), cand(3, 10, 0.5)]
    assert [c.juego.appid for c in elegir(cands, centavos(100), 5)] == [2, 3, 1]


@pytest.mark.parametrize("presupuesto", [0.01, 25, 61.5, 100, 137.77])
def test_coincide_con_fuerza_bruta(presupuesto):
    """La mochila da el mismo puntaje que probar todas las combinaciones posibles."""
    precios = [12.5, 30, 7.99, 45, 18.2, 60, 25.01, 9.99]
    puntajes = [0.3, 0.8, 0.1, 0.9, 0.4, 0.95, 0.6, 0.2]
    cands = [cand(i, p, s) for i, (p, s) in enumerate(zip(precios, puntajes, strict=True), start=1)]
    tope = centavos(presupuesto)

    mejor = max(
        (sum(c.puntaje for c in combo)
         for k in range(0, 4) for combo in itertools.combinations(cands, k)
         if sum(c.juego.precio_centavos for c in combo) <= tope),
    )
    elegidos = elegir(cands, tope, 3)
    assert sum(c.juego.precio_centavos for c in elegidos) <= tope
    assert sum(c.puntaje for c in elegidos) == pytest.approx(mejor)
