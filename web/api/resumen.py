"""Resumen de una lista de compra: cuánto se gasta, cuánto sobra y qué tan aprovechado queda el presupuesto."""
from collections import Counter
from dataclasses import dataclass

from web.api.recomendador import Candidato

# Si sobra menos de este porcentaje, el presupuesto se considera bien aprovechado.
HOLGURA_AJUSTADA = 0.10


@dataclass(frozen=True)
class Resumen:
    total_centavos: int
    restante_centavos: int
    porcentaje_usado: float
    mas_caro: int | None        # appid del juego más caro de la lista
    etiqueta_principal: str | None
    aprovechamiento: str        # "vacia", "ajustada" u "holgada"


def resumir(elegidos: list[Candidato], presupuesto_centavos: int) -> Resumen:
    if presupuesto_centavos <= 0:
        raise ValueError("el presupuesto debe ser mayor que 0")

    total = sum(c.juego.precio_centavos for c in elegidos)
    if total > presupuesto_centavos:
        raise ValueError("la lista se pasa del presupuesto")
    restante = presupuesto_centavos - total

    if not elegidos:
        return Resumen(0, presupuesto_centavos, 0.0, None, None, "vacia")

    mas_caro = max(elegidos, key=lambda c: (c.juego.precio_centavos, -c.juego.appid)).juego.appid

    conteo = Counter(e for c in elegidos for e in c.juego.etiquetas)
    etiqueta = None
    if conteo:
        # A igual cantidad gana la primera en orden alfabético, para que la respuesta no cambie.
        etiqueta = min(conteo, key=lambda e: (-conteo[e], e))

    if restante <= presupuesto_centavos * HOLGURA_AJUSTADA:
        aprovechamiento = "ajustada"
    else:
        aprovechamiento = "holgada"

    return Resumen(
        total_centavos=total,
        restante_centavos=restante,
        porcentaje_usado=round(total / presupuesto_centavos * 100, 2),
        mas_caro=mas_caro,
        etiqueta_principal=etiqueta,
        aprovechamiento=aprovechamiento,
    )
