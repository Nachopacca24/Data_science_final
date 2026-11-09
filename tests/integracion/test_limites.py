"""Valores límite: los dos lados de cada límite (ver CASOS.md, sección 2)."""
import pytest

from conftest import PRESUPUESTO_MAX, MAX_FAVORITOS


# ---------- presupuesto ----------

@pytest.mark.parametrize("caso, presupuesto, codigo", [
    ("VL-01 justo en cero (fuera)", 0, 422),
    ("VL-02 un centavo (dentro)", 0.01, 200),
    ("VL-03 justo en el máximo (dentro)", PRESUPUESTO_MAX, 200),
    ("VL-04 un centavo más del máximo (fuera)", round(PRESUPUESTO_MAX + 0.01, 2), 422),
])
def test_limites_presupuesto(api, cuerpo_valido, caso, presupuesto, codigo):
    cuerpo_valido["presupuesto"] = presupuesto
    assert api.post("/recomendaciones", json=cuerpo_valido).status_code == codigo, caso


def test_VL02_un_centavo_no_alcanza_para_nada(api, cuerpo_valido):
    """VL-02 · con Q0.01 la respuesta es válida pero la lista queda vacía."""
    cuerpo_valido["presupuesto"] = 0.01
    assert api.post("/recomendaciones", json=cuerpo_valido).json()["juegos"] == []


# ---------- cantidad de favoritos ----------

@pytest.mark.parametrize("caso, n, codigo", [
    ("VL-05 cero favoritos (fuera)", 0, 422),
    ("VL-06 un favorito (dentro)", 1, 200),
    ("VL-07 justo en el máximo (dentro)", MAX_FAVORITOS, 200),
    ("VL-08 uno más del máximo (fuera)", MAX_FAVORITOS + 1, 422),
])
def test_limites_favoritos(api, catalogo, caso, n, codigo):
    favoritos = [j["appid"] for j in catalogo[:n]]
    r = api.post("/recomendaciones", json={"presupuesto": 300, "favoritos": favoritos})
    assert r.status_code == codigo, caso


# ---------- un juego cabe justo / no cabe por un centavo ----------

@pytest.fixture(scope="module")
def mas_barato(catalogo):
    """El juego de pago más barato que pasa el umbral de calidad."""
    candidatos = [j for j in catalogo if j["pasa_umbral"] and j["precio_gtq"] > 0]
    return min(candidatos, key=lambda j: j["precio_gtq"])


def _favorito_distinto(catalogo, appid):
    return next(j["appid"] for j in catalogo if j["appid"] != appid)


def test_VL09_presupuesto_igual_al_precio_entra(api, catalogo, mas_barato):
    """VL-09 · presupuesto exactamente igual al precio -> el juego cabe y aparece."""
    r = api.post("/recomendaciones", json={
        "presupuesto": mas_barato["precio_gtq"],
        "favoritos": [_favorito_distinto(catalogo, mas_barato["appid"])],
    })
    assert mas_barato["appid"] in [j["appid"] for j in r.json()["juegos"]]


def test_VL10_un_centavo_menos_no_entra(api, catalogo, mas_barato):
    """VL-10 · presupuesto un centavo menor que el precio -> el juego ya no cabe."""
    r = api.post("/recomendaciones", json={
        "presupuesto": round(mas_barato["precio_gtq"] - 0.01, 2),
        "favoritos": [_favorito_distinto(catalogo, mas_barato["appid"])],
    })
    assert mas_barato["appid"] not in [j["appid"] for j in r.json()["juegos"]]
