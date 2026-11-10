"""Casos que salen del contrato oficial (web/CONTRATO_API.md), ver CASOS.md, sección 4.

Mismas técnicas que el resto: partición de equivalencia (PE), valores límite (VL) y tabla de
decisión (TD). Además se revisan las invariantes del formato de errores y de la respuesta.
"""
import pytest

from conftest import APPID_INEXISTENTE, LIMITE_BUSQUEDA_MAX, MAX_BUSCAR, MAX_JUEGOS_LISTA, PRESUPUESTO_MAX


def _assert_error(r, estado, error):
    """Todos los errores tienen el mismo formato: {error, mensaje, detalles[{campo, problema}]}."""
    assert r.status_code == estado, r.text
    cuerpo = r.json()
    assert set(cuerpo) == {"error", "mensaje", "detalles"}, cuerpo
    assert cuerpo["error"] == error
    assert cuerpo["mensaje"]
    for d in cuerpo["detalles"]:
        assert set(d) == {"campo", "problema"}, d
    return cuerpo


def _campos(cuerpo):
    return {d["campo"] for d in cuerpo["detalles"]}


# ---------- 4.1 partición de equivalencia: entrada estricta ----------

@pytest.mark.parametrize("caso, presupuesto", [
    ("PE-15 número como texto", "300"),
    ("PE-16 booleano", True),
])
def test_presupuesto_de_otro_tipo(api, cuerpo_valido, caso, presupuesto):
    """PE-15 y PE-16 · el presupuesto no se convierte de otro tipo: "300" o true -> 422 en el campo presupuesto."""
    cuerpo_valido["presupuesto"] = presupuesto
    cuerpo = _assert_error(api.post("/recomendaciones", json=cuerpo_valido), 422, "entrada_invalida")
    assert "presupuesto" in _campos(cuerpo), caso


def test_PE17_appid_favorito_como_texto(api, cuerpo_valido, un_appid):
    """PE-17 · un appid escrito como texto ("379720") no se convierte a número -> 422."""
    cuerpo_valido["favoritos"] = [str(un_appid)]
    _assert_error(api.post("/recomendaciones", json=cuerpo_valido), 422, "entrada_invalida")


def test_PE18_favoritos_repetidos(api, cuerpo_valido, un_appid):
    """PE-18 · el mismo favorito dos veces -> 422 en el campo favoritos."""
    cuerpo_valido["favoritos"] = [un_appid, un_appid]
    cuerpo = _assert_error(api.post("/recomendaciones", json=cuerpo_valido), 422, "entrada_invalida")
    assert "favoritos" in _campos(cuerpo)


def test_PE19_campo_que_no_esta_en_el_contrato(api, cuerpo_valido):
    """PE-19 · un campo extra no se ignora en silencio -> 422 que nombra ese campo."""
    cuerpo_valido["descuento"] = 0.75
    cuerpo = _assert_error(api.post("/recomendaciones", json=cuerpo_valido), 422, "entrada_invalida")
    assert "descuento" in _campos(cuerpo)


def test_PE20_cuerpo_que_no_es_json(api):
    """PE-20 · el cuerpo no se puede leer como JSON -> 422 en el campo cuerpo."""
    r = api.post("/recomendaciones", data="presupuesto=300", headers={"Content-Type": "application/json"})
    cuerpo = _assert_error(r, 422, "entrada_invalida")
    assert "cuerpo" in _campos(cuerpo)


def test_PE21_favorito_inexistente_dice_cual(api, catalogo):
    """PE-21 · con dos favoritos y solo el segundo inexistente, el error señala favoritos.1."""
    r = api.post("/recomendaciones", json={"presupuesto": 300,
                                           "favoritos": [catalogo[0]["appid"], APPID_INEXISTENTE]})
    cuerpo = _assert_error(r, 422, "entrada_invalida")
    assert _campos(cuerpo) == {"favoritos.1"}


def test_PE22_metodo_no_permitido(api):
    """PE-22 · GET a una ruta que solo acepta POST -> 405."""
    _assert_error(api.get("/recomendaciones"), 405, "metodo_no_permitido")


def test_PE23_ruta_inexistente(api):
    """PE-23 · una ruta que no existe -> 404 con el mismo formato de error."""
    _assert_error(api.get("/no-existe"), 404, "no_encontrado")


def test_PE13_juego_inexistente_con_formato(api):
    """PE-13 (complemento) · el 404 de un juego que no existe también trae el formato común."""
    _assert_error(api.get(f"/juegos/{APPID_INEXISTENTE}"), 404, "no_encontrado")


# ---------- 4.2 partición de equivalencia: búsqueda ----------

def test_PE24_busqueda_con_coincidencias(api, catalogo):
    """PE-24 · buscar un texto que existe: todos los resultados lo contienen (sin importar
    mayúsculas) y vienen en orden alfabético."""
    texto = catalogo[0]["nombre"][:3].upper()
    r = api.get("/juegos", params={"buscar": texto, "limite": LIMITE_BUSQUEDA_MAX})
    assert r.status_code == 200
    nombres = [j["nombre"] for j in r.json()]
    assert nombres, texto
    assert all(texto.casefold() in n.casefold() for n in nombres)
    assert [n.casefold() for n in nombres] == sorted(n.casefold() for n in nombres)


def test_PE25_busqueda_sin_coincidencias(api):
    """PE-25 · buscar un texto que no está en ningún nombre -> 200 con lista vacía (no 404)."""
    r = api.get("/juegos", params={"buscar": "zzqqxx-no-existe"})
    assert r.status_code == 200
    assert r.json() == []


# ---------- 4.3 valores límite ----------

@pytest.mark.parametrize("caso, presupuesto, codigo", [
    ("VL-11 dos decimales (dentro)", 300.01, 200),
    ("VL-12 tres decimales (fuera)", 300.001, 422),
])
def test_limite_decimales(api, cuerpo_valido, caso, presupuesto, codigo):
    """VL-11 y VL-12 · el presupuesto admite centavos, no fracciones de centavo."""
    cuerpo_valido["presupuesto"] = presupuesto
    assert api.post("/recomendaciones", json=cuerpo_valido).status_code == codigo, caso


@pytest.mark.parametrize("caso, limite, codigo", [
    ("VL-13 cero (fuera)", 0, 422),
    ("VL-14 uno (dentro)", 1, 200),
    ("VL-15 justo en el máximo (dentro)", LIMITE_BUSQUEDA_MAX, 200),
    ("VL-16 uno más del máximo (fuera)", LIMITE_BUSQUEDA_MAX + 1, 422),
])
def test_limite_de_busqueda(api, caso, limite, codigo):
    """VL-13 a VL-16 · `limite` va de 1 a LIMITE_BUSQUEDA_MAX y nunca devuelve más que eso."""
    r = api.get("/juegos", params={"limite": limite})
    assert r.status_code == codigo, caso
    if codigo == 200:
        assert len(r.json()) <= limite


@pytest.mark.parametrize("caso, largo, codigo", [
    ("VL-17 justo en el máximo (dentro)", MAX_BUSCAR, 200),
    ("VL-18 un carácter más (fuera)", MAX_BUSCAR + 1, 422),
])
def test_limite_largo_de_buscar(api, caso, largo, codigo):
    """VL-17 y VL-18 · el texto de búsqueda admite hasta MAX_BUSCAR caracteres."""
    r = api.get("/juegos", params={"buscar": "a" * largo})
    assert r.status_code == codigo, caso


def test_VL19_lista_nunca_pasa_de_cinco(api, catalogo):
    """VL-19 · con el presupuesto máximo y el máximo de favoritos alcanzaría para muchos juegos,
    pero la lista tiene como máximo MAX_JUEGOS_LISTA."""
    favoritos = [j["appid"] for j in catalogo[:5]]
    r = api.post("/recomendaciones", json={"presupuesto": PRESUPUESTO_MAX, "favoritos": favoritos})
    assert r.status_code == 200
    assert 0 < len(r.json()["juegos"]) <= MAX_JUEGOS_LISTA


# ---------- 4.4 tabla de decisión: regla de los juegos gratis ----------

def test_R5_no_recomienda_juegos_gratis(api, catalogo):
    """TD-R5 · C4 = gratis -> no entra, aunque pase el umbral y cabe (cuesta Q0).
    Se usan como favoritos juegos gratis, para que los más parecidos también tiendan a serlo."""
    gratis = [j["appid"] for j in catalogo if j["precio_gtq"] == 0][:5]
    if not gratis:
        pytest.skip("el catálogo no tiene juegos gratis")
    r = api.post("/recomendaciones", json={"presupuesto": 300, "favoritos": gratis})
    assert r.status_code == 200
    juegos = r.json()["juegos"]
    assert juegos, "con Q300 debería haber juegos de pago que cumplan todo"
    assert all(j["precio_gtq"] > 0 for j in juegos), juegos


# ---------- 4.5 invariantes de la respuesta ----------

@pytest.fixture(scope="module")
def peticion(catalogo):
    return {"presupuesto": 300, "favoritos": [j["appid"] for j in catalogo[:2]]}


def test_lista_ordenada_por_puntaje(api, peticion):
    """La lista va de mayor a menor puntaje."""
    puntajes = [j["puntaje"] for j in api.post("/recomendaciones", json=peticion).json()["juegos"]]
    assert puntajes == sorted(puntajes, reverse=True)


def test_misma_peticion_misma_respuesta(api, peticion):
    """La misma petición da siempre la misma respuesta (no hay azar ni depende del orden de llegada)."""
    primera = api.post("/recomendaciones", json=peticion).json()
    for _ in range(3):
        assert api.post("/recomendaciones", json=peticion).json() == primera


def test_presupuesto_se_devuelve_en_la_respuesta(api, peticion):
    """El presupuesto de la respuesta es el que se pidió."""
    assert api.post("/recomendaciones", json=peticion).json()["presupuesto"] == peticion["presupuesto"]
