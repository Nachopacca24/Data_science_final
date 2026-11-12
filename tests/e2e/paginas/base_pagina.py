"""Base de todos los page objects.

Principio abierto/cerrado (ver DECISIONES.md): una pantalla nueva hereda de BasePagina,
define su RUTA y ya sabe abrirse y leer el pie de página; esta clase no se modifica.
"""
from playwright.sync_api import Page, expect


class BasePagina:
    RUTA = "/"

    def __init__(self, page: Page):
        self.page = page

    def abrir(self):
        self.page.goto(self.RUTA)
        return self

    def version_mostrada(self) -> str:
        """Texto del pie, p. ej. 'versión 1a2b3c4 · dev'. Lo pinta la pantalla con lo que responde /version."""
        pie = self.page.locator("#version")
        expect(pie).to_contain_text("versión")  # espera a que la pantalla reciba la respuesta de la API
        return pie.inner_text()
