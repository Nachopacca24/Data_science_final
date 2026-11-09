"""Pruebas unitarias: el catálogo se valida al cargarlo y la configuración de la instancia es correcta."""
import pytest

from web.api import config
from web.api.catalogo import catalogo, leer

ENCABEZADO = "appid,nombre,precio_gtq,etiquetas,generos,p_bien_recibido,pasa_umbral,pct_positivo,imagen\n"
FILA_OK = "10,Counter-Strike,38.3,Action|FPS,Action,0.75,True,0.97,https://x/10.jpg\n"


def csv(tmp_path, *filas):
    ruta = tmp_path / "catalogo.csv"
    ruta.write_text(ENCABEZADO + "".join(filas), encoding="utf-8")
    return ruta


# ---------- catálogo real ----------

def test_catalogo_demo_carga_y_tiene_de_ambos_tipos():
    cat = catalogo()
    assert len(cat) >= 100
    assert any(j.pasa_umbral for j in cat.values()) and not all(j.pasa_umbral for j in cat.values())
    assert any(j.precio_gtq > 0 for j in cat.values())


# ---------- catálogo dañado: la API no debe arrancar con él ----------

def test_lee_una_fila_valida(tmp_path):
    j = leer(csv(tmp_path, FILA_OK))[10]
    assert j.etiquetas == ("Action", "FPS") and j.pasa_umbral is True and j.precio_centavos == 3830


@pytest.mark.parametrize("fila, motivo", [
    ("abc,X,1,,,0.5,True,0.5,\n", "appid no numérico"),
    ("10,X,1,,,0.5,Sí,0.5,\n", "booleano mal escrito"),
    ("10,X,-1,,,0.5,True,0.5,\n", "precio negativo"),
    ("10,X,1,,,1.5,True,0.5,\n", "probabilidad fuera de 0 a 1"),
])
def test_rechaza_filas_invalidas(tmp_path, fila, motivo):
    with pytest.raises(ValueError, match="fila 2"):
        leer(csv(tmp_path, fila))


def test_rechaza_appid_repetido(tmp_path):
    with pytest.raises(ValueError, match="repetido"):
        leer(csv(tmp_path, FILA_OK, FILA_OK))


def test_rechaza_catalogo_vacio(tmp_path):
    with pytest.raises(ValueError, match="vacío"):
        leer(csv(tmp_path))


# ---------- versión y ambiente ----------

def test_version_por_variable_de_entorno(monkeypatch):
    monkeypatch.setenv("APP_VERSION", "abc1234")
    assert config.version() == "abc1234"


def test_version_por_archivo_del_build(monkeypatch, tmp_path):
    monkeypatch.delenv("APP_VERSION", raising=False)
    archivo = tmp_path / "VERSION"
    archivo.write_text("def5678\n")
    monkeypatch.setattr(config, "ARCHIVO_VERSION", archivo)
    assert config.version() == "def5678"


def test_version_sin_build_es_local(monkeypatch, tmp_path):
    monkeypatch.delenv("APP_VERSION", raising=False)
    monkeypatch.setattr(config, "ARCHIVO_VERSION", tmp_path / "no-existe")
    assert config.version() == "local"


@pytest.mark.parametrize("valor, esperado", [(None, "dev"), ("dev", "dev"), ("PROD", "prod")])
def test_ambiente_valido(monkeypatch, valor, esperado):
    if valor is None:
        monkeypatch.delenv("APP_AMBIENTE", raising=False)
    else:
        monkeypatch.setenv("APP_AMBIENTE", valor)
    assert config.ambiente() == esperado


def test_ambiente_desconocido_detiene_el_arranque(monkeypatch):
    monkeypatch.setenv("APP_AMBIENTE", "produccion")
    with pytest.raises(ValueError, match="APP_AMBIENTE"):
        config.ambiente()
