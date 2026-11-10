"""Pruebas unitarias de la selección de juegos dentro del presupuesto (Fabiola).

Complementan test_recomendador.py con los casos que pide la parte C: presupuesto exacto,
juego que no cabe, catálogo vacío y empates.
"""
from web.api.catalogo import Juego
from web.api.recomendador import Candidato, candidatos, elegir


def juego(appid, precio=10.0, p=0.9, pasa=True, etiquetas=("Action",)):
    return Juego(appid=appid, nombre=f"Juego {appid}", precio_gtq=precio, etiquetas=tuple(etiquetas),
                 generos=(), p_bien_recibido=p, pasa_umbral=pasa, pct_positivo=0.9, imagen="")


def cand(appid, precio, puntaje):
    return Candidato(juego(appid, precio=precio, p=puntaje), similitud=1.0)


def ids(elegidos):
    return [c.juego.appid for c in elegidos]


# ---------- presupuesto exacto ----------

def test_dos_juegos_que_suman_justo_el_presupuesto_caben():
    # Q25.50 + Q74.50 = Q100.00: con Q100 entran los dos.
    assert sorted(ids(elegir([cand(1, 25.50, 0.5), cand(2, 74.50, 0.5)], 10_000, 5))) == [1, 2]


def test_si_la_suma_se_pasa_un_centavo_solo_entra_uno():
    elegidos = elegir([cand(1, 25.51, 0.5), cand(2, 74.50, 0.6)], 10_000, 5)
    assert ids(elegidos) == [2]


# ---------- juego que no cabe ----------

def test_juego_mas_caro_que_el_presupuesto_se_descarta_aunque_sea_el_mejor():
    cands = [cand(1, 500, 0.99), cand(2, 40, 0.3), cand(3, 50, 0.2)]
    assert sorted(ids(elegir(cands, 10_000, 5))) == [2, 3]


def test_si_ningun_juego_cabe_la_lista_queda_vacia():
    assert elegir([cand(1, 60, 0.9), cand(2, 80, 0.8)], 5_000, 5) == []


# ---------- catálogo vacío ----------

def test_catalogo_vacio_no_da_candidatos():
    assert candidatos({}, [juego(1)]) == []


def test_catalogo_vacio_da_lista_vacia_con_cualquier_presupuesto():
    assert elegir(candidatos({}, [juego(1)]), 1_000_000, 5) == []


def test_catalogo_sin_juegos_elegibles_se_comporta_como_vacio():
    fav = juego(1)
    cat = {j.appid: j for j in [fav, juego(2, pasa=False), juego(3, precio=0)]}
    assert elegir(candidatos(cat, [fav]), 10_000, 5) == []
