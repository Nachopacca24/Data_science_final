
"""Page object de la zona de resultados y de los mensajes de error.

Responsabilidad única: leer lo que la pantalla muestra después de enviar. No sabe cómo se llena
el formulario (eso es de BusquedaPagina). Siempre se llama primero a un `esperar_*`, porque la
respuesta de la API llega después del clic.
"""
import re

from playwright.sync_api import expect

from paginas.base_pagina import BasePagina


def _quetzales(texto: str) -> float:
    """'Q284.30' -> 284.3"""
    return float(texto.replace("Q", "").replace(",", "").strip())


class ResultadosPagina(BasePagina):
    # --- localizadores ---
    def _seccion(self):
        return self.page.locator("#resultado")

    def _tarjetas(self):
        return self.page.locator("#lista > li")

    def _mensaje_vacio(self):
        return self.page.locator("#vacia")

    def _error(self):
        return self.page.get_by_role("alert")

    # --- esperas ---
    def esperar_lista(self):
        expect(self._tarjetas().first).to_be_visible()
        return self

    def esperar_lista_vacia(self):
        expect(self._mensaje_vacio()).to_be_visible()
        expect(self._tarjetas()).to_have_count(0)
        return self

    def esperar_error(self, patron: str):
        expect(self._error()).to_have_text(re.compile(patron, re.I))
        return self

    # --- lecturas ---
    def cantidad_juegos(self) -> int:
        return self._tarjetas().count()

    def nombres(self) -> list[str]:
        return self.page.locator("#lista li strong").all_inner_texts()

    def total_gtq(self) -> float:
        return _quetzales(self.page.locator("#r-total").inner_text())

    def restante_gtq(self) -> float:
        return _quetzales(self.page.locator("#r-restante").inner_text())

    def verificar_sin_resultados(self):
        """Nunca debe quedar una lista visible junto a un error."""
        expect(self._seccion()).to_be_hidden()
        return self
