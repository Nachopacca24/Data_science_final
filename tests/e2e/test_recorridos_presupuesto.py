"""Recorridos de regresión: presupuesto inválido, presupuesto insuficiente y envío sin favoritos."""
import pytest

FAVORITO = "DOOM"  # debe existir en web/catalogo_demo.csv


@pytest.mark.parametrize("presupuesto", ["0", "-50"])
def test_presupuesto_invalido_muestra_error_y_no_lista(busqueda, resultados, presupuesto):
    busqueda.agregar_favorito(FAVORITO).fijar_presupuesto(presupuesto).enviar()

    resultados.esperar_error(r"mayor que cero")
    resultados.verificar_sin_resultados()


def test_presupuesto_insuficiente_avisa_que_no_alcanza(busqueda, resultados):
    busqueda.agregar_favorito(FAVORITO).fijar_presupuesto("0.01").enviar()  # Q0.01 no alcanza (VL-02 de CASOS.md)

    resultados.esperar_lista_vacia()
    assert resultados.cantidad_juegos() == 0
    assert resultados.total_gtq() == 0
    assert resultados.restante_gtq() == pytest.approx(0.01)  # no se gastó nada


def test_enviar_sin_favoritos_pide_elegir_uno(busqueda, resultados):
    busqueda.fijar_presupuesto(300).enviar()

    resultados.esperar_error(r"al menos un juego")
    resultados.verificar_sin_resultados()
