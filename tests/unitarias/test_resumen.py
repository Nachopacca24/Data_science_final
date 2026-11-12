"""Pruebas unitarias del resumen de la lista de compra."""
import pytest

from web.api.catalogo import Juego
from web.api.recomendador import Candidato
from web.api.resumen import resumir


def cand(appid, precio, etiquetas=("Action",)):
    j = Juego(appid=appid, nombre=f"Juego {appid}", precio_gtq=precio, etiquetas=tuple(etiquetas),
              generos=(), p_bien_recibido=0.9, pasa_umbral=True, pct_positivo=0.9, imagen="")
    return Candidato(j, similitud=1.0)


def test_lista_vacia_deja_todo_el_presupuesto():
    r = resumir([], 30_000)
    assert (r.total_centavos, r.restante_centavos, r.aprovechamiento) == (0, 30_000, "vacia")
    assert r.mas_caro is None and r.etiqueta_principal is None


def test_total_restante_y_porcentaje():
    r = resumir([cand(1, 100), cand(2, 50)], 30_000)
    assert (r.total_centavos, r.restante_centavos, r.porcentaje_usado) == (15_000, 15_000, 50.0)


def test_sobra_justo_el_diez_por_ciento_es_ajustada():
    assert resumir([cand(1, 270)], 30_000).aprovechamiento == "ajustada"


def test_sobra_un_centavo_mas_del_diez_por_ciento_es_holgada():
    assert resumir([cand(1, 269.99)], 30_000).aprovechamiento == "holgada"


def test_mas_caro_y_en_empate_gana_el_appid_menor():
    assert resumir([cand(5, 40), cand(3, 60), cand(9, 60)], 30_000).mas_caro == 3


def test_etiqueta_principal_y_desempate_alfabetico():
    assert resumir([cand(1, 10, ("FPS", "Gore")), cand(2, 10, ("FPS",))], 30_000).etiqueta_principal == "FPS"
    assert resumir([cand(1, 10, ("Rogue",)), cand(2, 10, ("Action",))], 30_000).etiqueta_principal == "Action"


def test_juegos_sin_etiquetas_no_tienen_etiqueta_principal():
    assert resumir([cand(1, 10, ())], 30_000).etiqueta_principal is None


@pytest.mark.parametrize("presupuesto", [0, -100])
def test_presupuesto_no_positivo_es_error(presupuesto):
    with pytest.raises(ValueError):
        resumir([], presupuesto)


def test_lista_que_se_pasa_del_presupuesto_es_error():
    with pytest.raises(ValueError):
        resumir([cand(1, 100)], 9_999)
