# Sugerencias de IA

Sugerencias que hizo un asistente de IA durante el proyecto, qué se hizo con cada una y cómo se comprobó. Cada quien agrega las suyas con su nombre.

| # | Quién | Asistente |
|---|---|---|
| IA-1 a IA-3 | Mati | Claude (Claude Code) |

## IA-1 · La mochila en centavos, no en quetzales redondeados (Mati)

**Sugerencia.** El notebook 05 redondea los precios al quetzal **hacia arriba** antes de la mochila. La IA advirtió que así un juego que cuesta justo el presupuesto (p. ej. Q38.30 con Q38.30) queda fuera, y eso rompe el caso VL-09 de `CASOS.md`. Propuso trabajar en **centavos enteros**, con una mochila exacta (frontera de Pareto).

**Decisión.** Se aceptó. Está en `web/api/recomendador.py` (DECISIONES A4).

**Comprobación.**
- `test_precio_igual_al_presupuesto_cabe` y `test_un_centavo_menos_ya_no_cabe`.
- `test_coincide_con_fuerza_bruta`, que compara el resultado con todas las combinaciones posibles.
- Los casos VL-09 y VL-10 de Pacca pasan.
- Al cambiar `<=` por `<` a propósito, fallan 3 pruebas.

## IA-2 · Entrada estricta: `"300"` no es un presupuesto válido (Mati)

**Sugerencia.** Por defecto, FastAPI/pydantic convierte `"300"` (texto) en `300` y `true` en `1`, así que esas peticiones pasarían como válidas. La IA propuso tipos estrictos (`StrictFloat`, `StrictInt`), un máximo de 2 decimales, rechazar favoritos repetidos y campos extra, y un **formato único de error en español**.

**Decisión.** Se aceptó y quedó en el contrato oficial (`web/CONTRATO_API.md`, DECISIONES A7 y A8).

**Comprobación.**
- 48 pruebas en `test_entrada_api.py`, entre ellas `"300"`, `true`, `300.001`, `[379720, 379720]` y `{"descuento": 0.9}` → `422`.
- Al aceptar presupuesto 0 a propósito, la prueba falla.

## IA-3 · No editar las pruebas de otro para que pase el lint (Mati)

**Sugerencia.** Al activar `ruff`, aparecieron avisos en `tests/integracion/` (de Pacca). Uno era falso: ruff creía que `conftest` era una librería externa, y eso se arregló en la configuración (`known-first-party`). Los otros 2 eran de estilo de verdad. La IA propuso **no editar el código de otro integrante sin avisarle**: dejar esa carpeta fuera del lint por ahora y avisar.

**Decisión.** Se aceptó. Se avisó a Pacca, y él mismo arregló sus 2 avisos y metió `tests/integracion/` al lint en su commit `d5e41ca` (DECISIONES P4).

**Comprobación.** Las 34 pruebas de integración de Pacca corrieron sin cambios contra la API (corrida 42737504756), y ahora `ruff check .` pasa con todo el código de pruebas incluido.

## Lo que la IA hizo mal y se corrigió

Para que conste que las sugerencias se revisaron y no se aceptaron a ciegas:
- La primera versión de la pantalla dejaba la lista anterior visible al lado de un mensaje de error. Se encontró al probar la pantalla en el navegador y se corrigió: ahora la lista se oculta.
- La primera versión de la API no arrancaba: el formato de `responses` estaba mal. Se encontró al levantarla y se corrigió antes del primer commit.
