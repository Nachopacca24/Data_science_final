"""Recorrido 1 (smoke): una persona elige dos favoritos, pide su lista y la ve completa."""
import os

import pytest

FAVORITOS = ["DOOM", "Hades"]  # deben existir en web/catalogo_demo.csv
PRESUPUESTO = 300
MAX_JUEGOS_LISTA = 5  # contrato de la API: la lista final tiene como máximo 5 juegos


@pytest.mark.smoke
def test_lista_completa_dentro_del_presupuesto(busqueda, resultados):
    for nombre in FAVORITOS:
        busqueda.agregar_favorito(nombre)
    busqueda.fijar_presupuesto(PRESUPUESTO).enviar()

    resultados.esperar_lista()
    assert 1 <= resultados.cantidad_juegos() <= MAX_JUEGOS_LISTA
    assert len(set(resultados.nombres())) == resultados.cantidad_juegos()  # sin juegos repetidos
    assert resultados.total_gtq() <= PRESUPUESTO
    assert resultados.total_gtq() + resultados.restante_gtq() == pytest.approx(PRESUPUESTO, abs=0.01)


@pytest.mark.smoke
def test_pie_muestra_version_y_ambiente_del_despliegue(busqueda):
    """La pantalla probada es la instancia desplegada: el pie trae el SHA y el ambiente que responde /version."""
    pie = busqueda.version_mostrada()
    print(f"pie de la pantalla: {pie}")  # queda en el log del build
    if sha := os.environ.get("SHA_ESPERADO"):
        assert sha[:7] in pie
    if ambiente := os.environ.get("AMBIENTE"):
        assert pie.endswith(ambiente)
