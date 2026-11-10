"""Partición de equivalencia: un caso por clase válida o inválida (ver CASOS.md, sección 1)."""
import pytest

from conftest import APPID_INEXISTENTE

# ---------- smoke: la API está viva ----------

@pytest.mark.smoke
def test_salud_responde_ok(api):
    """Smoke: el servicio está levantado."""
    r = api.get("/salud")
    assert r.status_code == 200
    assert r.json()["estado"] == "ok"


@pytest.mark.smoke
def test_version_dice_sha_y_ambiente(api):
    """Smoke: la instancia informa qué versión y ambiente es."""
    cuerpo = api.get("/version").json()
    print(f"version={cuerpo['version']} ambiente={cuerpo['ambiente']}")
    assert cuerpo["version"]
    assert cuerpo["ambiente"] in {"dev", "prod"}


# ---------- presupuesto ----------

@pytest.mark.smoke
def test_PE01_presupuesto_valido(api, cuerpo_valido):
    """PE-01 · clase válida: presupuesto = 300."""
    r = api.post("/recomendaciones", json=cuerpo_valido)
    assert r.status_code == 200
    assert isinstance(r.json()["juegos"], list)


@pytest.mark.parametrize("caso, presupuesto", [
    ("PE-02 negativo", -50),
    ("PE-03 cero", 0),
    ("PE-04 no numérico", "trescientos"),
    ("PE-06 nulo", None),
])
def test_presupuesto_invalido(api, cuerpo_valido, caso, presupuesto):
    """PE-02 a PE-06 · clases inválidas de presupuesto -> 422."""
    cuerpo_valido["presupuesto"] = presupuesto
    assert api.post("/recomendaciones", json=cuerpo_valido).status_code == 422, caso


def test_PE05_presupuesto_ausente(api, cuerpo_valido):
    """PE-05 · clase inválida: falta el campo presupuesto."""
    del cuerpo_valido["presupuesto"]
    assert api.post("/recomendaciones", json=cuerpo_valido).status_code == 422


# ---------- favoritos ----------

def test_PE07_favorito_existente(api, cuerpo_valido):
    """PE-07 · clase válida: un favorito que existe."""
    assert api.post("/recomendaciones", json=cuerpo_valido).status_code == 200


@pytest.mark.parametrize("caso, favoritos", [
    ("PE-08 lista vacía", []),
    ("PE-09 appid inexistente", [APPID_INEXISTENTE]),
    ("PE-10 appid no numérico", ["abc"]),
])
def test_favoritos_invalidos(api, cuerpo_valido, caso, favoritos):
    """PE-08 a PE-10 · clases inválidas de favoritos -> 422."""
    cuerpo_valido["favoritos"] = favoritos
    assert api.post("/recomendaciones", json=cuerpo_valido).status_code == 422, caso


def test_PE11_favoritos_ausente(api, cuerpo_valido):
    """PE-11 · clase inválida: falta el campo favoritos."""
    del cuerpo_valido["favoritos"]
    assert api.post("/recomendaciones", json=cuerpo_valido).status_code == 422


# ---------- detalle de un juego ----------

def test_PE12_juego_existente(api, un_appid):
    """PE-12 · clase válida: el juego existe y devuelve el mismo appid."""
    r = api.get(f"/juegos/{un_appid}")
    assert r.status_code == 200
    assert r.json()["appid"] == un_appid


def test_PE13_juego_inexistente(api):
    """PE-13 · clase inválida: appid que no está en el catálogo -> 404."""
    assert api.get(f"/juegos/{APPID_INEXISTENTE}").status_code == 404


def test_PE14_juego_no_numerico(api):
    """PE-14 · clase inválida: appid no numérico -> 422."""
    assert api.get("/juegos/abc").status_code == 422
