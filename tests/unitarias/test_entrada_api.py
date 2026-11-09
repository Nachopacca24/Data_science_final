"""Pruebas unitarias: la API valida los datos de entrada y responde con el formato del contrato.

Corren sin levantar el servidor (TestClient de FastAPI) contra web/catalogo_demo.csv.
"""
import pytest
from fastapi.testclient import TestClient

from web.api import config
from web.api.catalogo import catalogo
from web.api.main import app

DOOM, HADES = 379720, 1145360


@pytest.fixture(scope="module")
def cliente():
    with TestClient(app) as c:
        yield c


def recomendar(cliente, **cuerpo):
    base = {"presupuesto": 300, "favoritos": [DOOM]}
    return cliente.post("/recomendaciones", json={**base, **cuerpo})


def assert_error(r, estado, error, campo=None):
    """Toda respuesta de error tiene error, mensaje y detalles; opcionalmente revisa el campo culpable."""
    assert r.status_code == estado, r.text
    cuerpo = r.json()
    assert set(cuerpo) == {"error", "mensaje", "detalles"}
    assert cuerpo["error"] == error
    if campo is not None:
        assert campo in [d["campo"] for d in cuerpo["detalles"]], cuerpo


# ---------- presupuesto ----------

@pytest.mark.parametrize("presupuesto", [300, 300.5, 0.01, config.PRESUPUESTO_MAX])
def test_presupuesto_valido(cliente, presupuesto):
    r = recomendar(cliente, presupuesto=presupuesto)
    assert r.status_code == 200, r.text
    assert r.json()["presupuesto"] == presupuesto


@pytest.mark.parametrize("presupuesto, motivo", [
    (0, "cero"),
    (-50, "negativo"),
    (config.PRESUPUESTO_MAX + 0.01, "pasa del máximo"),
    (300.001, "más de 2 decimales"),
    ("300", "número como texto"),
    ("trescientos", "texto"),
    (True, "booleano"),
    (None, "nulo"),
    ([300], "lista"),
])
def test_presupuesto_invalido(cliente, presupuesto, motivo):
    assert_error(recomendar(cliente, presupuesto=presupuesto), 422, "entrada_invalida", "presupuesto")


def test_presupuesto_ausente(cliente):
    r = cliente.post("/recomendaciones", json={"favoritos": [DOOM]})
    assert_error(r, 422, "entrada_invalida", "presupuesto")
    assert r.json()["detalles"][0]["problema"] == "falta este campo"


# ---------- favoritos ----------

def test_favoritos_en_el_maximo(cliente):
    cinco = sorted(catalogo())[: config.MAX_FAVORITOS]
    assert recomendar(cliente, favoritos=cinco).status_code == 200


@pytest.mark.parametrize("favoritos, motivo", [
    ([], "lista vacía"),
    ([DOOM, DOOM], "repetidos"),
    ([0], "appid cero"),
    ([-5], "appid negativo"),
    (["abc"], "texto"),
    ([str(DOOM)], "appid como texto"),
    ([True], "booleano"),
    ([379720.5], "decimal"),
    (DOOM, "no es lista"),
    (None, "nulo"),
])
def test_favoritos_invalidos(cliente, favoritos, motivo):
    r = recomendar(cliente, favoritos=favoritos)
    assert r.status_code == 422, motivo
    assert all(d["campo"].startswith("favoritos") for d in r.json()["detalles"]), r.json()


def test_favoritos_de_mas(cliente):
    seis = sorted(catalogo())[: config.MAX_FAVORITOS + 1]
    assert_error(recomendar(cliente, favoritos=seis), 422, "entrada_invalida", "favoritos")


def test_favorito_que_no_esta_en_el_catalogo(cliente):
    r = recomendar(cliente, favoritos=[DOOM, 999_999_999])
    assert_error(r, 422, "entrada_invalida", "favoritos.1")
    assert "999999999" in r.json()["detalles"][0]["problema"]


# ---------- cuerpo de la petición ----------

def test_campo_extra_no_permitido(cliente):
    assert_error(recomendar(cliente, descuento=0.9), 422, "entrada_invalida", "descuento")


@pytest.mark.parametrize("cuerpo", ["no es json", "[1, 2]", "null"])
def test_cuerpo_que_no_es_un_objeto(cliente, cuerpo):
    r = cliente.post("/recomendaciones", content=cuerpo, headers={"Content-Type": "application/json"})
    assert_error(r, 422, "entrada_invalida", "cuerpo")


# ---------- detalle y búsqueda de juegos ----------

def test_detalle_de_un_juego(cliente):
    r = cliente.get(f"/juegos/{DOOM}")
    assert r.status_code == 200
    j = r.json()
    assert j["appid"] == DOOM and j["nombre"] == "DOOM"
    assert {"precio_gtq", "etiquetas", "p_bien_recibido", "pasa_umbral"} <= set(j)


@pytest.mark.parametrize("appid", ["abc", "0", "-1", "1.5"])
def test_detalle_appid_invalido(cliente, appid):
    assert_error(cliente.get(f"/juegos/{appid}"), 422, "entrada_invalida", "appid")


def test_detalle_juego_inexistente(cliente):
    assert_error(cliente.get("/juegos/999999999"), 404, "no_encontrado")


def test_busqueda_sin_importar_mayusculas(cliente):
    nombres = [j["nombre"] for j in cliente.get("/juegos", params={"buscar": "doom"}).json()]
    assert "DOOM" in nombres and "DOOM Eternal" in nombres


def test_busqueda_respeta_el_limite(cliente):
    assert len(cliente.get("/juegos", params={"limite": 3}).json()) == 3


@pytest.mark.parametrize("params, campo", [
    ({"limite": 0}, "limite"),
    ({"limite": config.LIMITE_BUSQUEDA_MAX + 1}, "limite"),
    ({"limite": "diez"}, "limite"),
    ({"buscar": "x" * 101}, "buscar"),
])
def test_busqueda_parametros_invalidos(cliente, params, campo):
    assert_error(cliente.get("/juegos", params=params), 422, "entrada_invalida", campo)


# ---------- sistema ----------

def test_salud(cliente):
    assert cliente.get("/salud").json() == {"estado": "ok"}


def test_version_lee_sha_y_ambiente(cliente, monkeypatch):
    monkeypatch.setenv("APP_VERSION", "0a52f18")
    monkeypatch.setenv("APP_AMBIENTE", "prod")
    assert cliente.get("/version").json() == {"version": "0a52f18", "ambiente": "prod"}


def test_ruta_inexistente_usa_el_formato_de_error(cliente):
    assert_error(cliente.get("/no-existe"), 404, "no_encontrado")


def test_metodo_no_permitido_usa_el_formato_de_error(cliente):
    assert_error(cliente.get("/recomendaciones"), 405, "metodo_no_permitido")


def test_la_pantalla_se_sirve_en_la_raiz(cliente):
    r = cliente.get("/")
    assert r.status_code == 200 and "text/html" in r.headers["content-type"]
