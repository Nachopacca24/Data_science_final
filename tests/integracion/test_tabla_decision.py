"""Tabla de decisión: ¿un juego entra a la lista? (ver CASOS.md, sección 3)

| Regla | C1 pasa umbral | C2 cabe | C3 es favorito | Acción   |
|-------|----------------|---------|----------------|----------|
| R1    | No             | -       | -              | No entra |
| R2    | Sí             | No      | -              | No entra |
| R3    | Sí             | Sí      | Sí             | No entra |
| R4    | Sí             | Sí      | No             | Entra    |
"""
import pytest

PRESUPUESTO = 300


@pytest.fixture(scope="module")
def respuesta(api, catalogo):
    """Una recomendación con Q300 y un favorito que pasa el umbral y cabe (para cubrir R3)."""
    favorito = next(j for j in catalogo if j["pasa_umbral"] and 0 < j["precio_gtq"] <= PRESUPUESTO)
    r = api.post("/recomendaciones", json={"presupuesto": PRESUPUESTO, "favoritos": [favorito["appid"]]})
    assert r.status_code == 200
    return {"favorito": favorito, "cuerpo": r.json()}


def _detalle(api, appid):
    return api.get(f"/juegos/{appid}").json()


def test_R1_ninguno_bajo_el_umbral(api, respuesta):
    """R1 · C1 = No -> ningún juego recomendado está bajo el umbral de calidad."""
    for j in respuesta["cuerpo"]["juegos"]:
        assert _detalle(api, j["appid"])["pasa_umbral"], j


def test_R2_ninguno_mas_caro_que_el_presupuesto(respuesta):
    """R2 · C2 = No -> ningún juego cuesta más que el presupuesto."""
    for j in respuesta["cuerpo"]["juegos"]:
        assert j["precio_gtq"] <= PRESUPUESTO, j


def test_R3_no_recomienda_los_favoritos(respuesta):
    """R3 · C3 = Sí -> el favorito (que pasa el umbral y cabe) no aparece en la lista."""
    recomendados = [j["appid"] for j in respuesta["cuerpo"]["juegos"]]
    assert respuesta["favorito"]["appid"] not in recomendados


def test_R4_si_hay_candidatos_la_lista_no_esta_vacia(respuesta):
    """R4 · C1 = Sí, C2 = Sí, C3 = No -> con Q300 hay juegos que cumplen todo, así que la lista no queda vacía."""
    assert len(respuesta["cuerpo"]["juegos"]) > 0


# ---------- invariantes de toda respuesta válida ----------

def test_total_no_supera_el_presupuesto(respuesta):
    assert respuesta["cuerpo"]["total_gtq"] <= PRESUPUESTO


def test_restante_es_presupuesto_menos_total(respuesta):
    c = respuesta["cuerpo"]
    assert c["restante_gtq"] == pytest.approx(PRESUPUESTO - c["total_gtq"], abs=0.01)


def test_sin_juegos_repetidos(respuesta):
    appids = [j["appid"] for j in respuesta["cuerpo"]["juegos"]]
    assert len(appids) == len(set(appids))
