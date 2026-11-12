"""Page object del formulario: favoritos + presupuesto.

Responsabilidad única: llenar y enviar el formulario. No lee resultados (eso es de ResultadosPagina).
"""
from playwright.sync_api import expect

from paginas.base_pagina import BasePagina


class BusquedaPagina(BasePagina):
    RUTA = "/"  # la API sirve la pantalla en la raíz

    # --- localizadores: lo único que cambia si cambia el HTML ---
    def _campo_busqueda(self):
        return self.page.get_by_label("Juegos que te gustaron")

    def _favoritos_elegidos(self):
        return self.page.get_by_label("Favoritos elegidos").locator("li")

    def _campo_presupuesto(self):
        return self.page.get_by_label("Presupuesto (Q)")

    def _boton_enviar(self):
        return self.page.get_by_role("button", name="Recomendar")

    # --- acciones ---
    def agregar_favorito(self, nombre: str):
        """Escribe el nombre, espera la sugerencia exacta y la elige (así es como la pantalla acepta favoritos)."""
        antes = self._favoritos_elegidos().count()
        self._campo_busqueda().fill(nombre)
        self.page.get_by_role("option", name=nombre, exact=True).click()
        expect(self._favoritos_elegidos()).to_have_count(antes + 1)
        return self

    def fijar_presupuesto(self, valor):
        self._campo_presupuesto().fill(str(valor))
        return self

    def enviar(self):
        self._boton_enviar().click()
        return self
