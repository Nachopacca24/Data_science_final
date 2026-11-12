# Sugerencias de IA

Sugerencias que hizo un asistente de IA durante el proyecto, qué se hizo con cada una y cómo se comprobó. Cada quien agrega las suyas con su nombre.

| # | Quién | Asistente |
|---|---|---|
| IA-1 a IA-3 | Mati | Claude (Claude Code) |
| IA-4 | Fabiola | Claude (Claude Code) |
| IA-5 e IA-6 | JuanDa | Claude (chat) |

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

## IA-4 · La puerta de cobertura con source y omit, no con include (Fabiola)

**Sugerencia.** La primera versión de la puerta listaba los módulos de negocio con `include`. Al probar que la puerta sí detiene el build, la IA notó que corriendo solo `test_catalogo_y_config.py` la cobertura salía en 98 %: con `include`, un módulo que ninguna prueba importa no aparece en el reporte. Propuso medir con `source = ["web/api"]` y sacar con `omit` lo que no es negocio, para que un módulo sin pruebas cuente como 0 %.

**Decisión.** Se aceptó (DECISIONES U4).

**Comprobación.** Con la misma corrida parcial, la cobertura baja a 32 % y pytest termina con exit 1. Con todas las pruebas sale 100 % y pasa.

## IA-5 · Las e2e corren dentro de `desplegar.yml`, no en un job aparte (JuanDa)

**Sugerencia.** La primera propuesta de la IA fue un job `e2e` nuevo al final de `pipeline.yml`. Al leer `desplegar.yml`, la IA corrigió: el contenedor existe solo dentro del job `desplegar` (DECISIONES C4), así que otro job no podría alcanzar esa instancia sin desplegar una segunda. Propuso dos pasos nuevos en ese job, después de integración, y pasar el parámetro `navegador` desde `pipeline.yml`.

**Decisión.** Se aceptó (DECISIONES E5).

**Comprobación.**
- `pipeline.yml` pasa a `desplegar.yml` la suite y el navegador; después de integración, `desplegar.yml` instala el navegador seleccionado y ejecuta E2E contra la misma instancia desplegada.
- En la corrida #17, el log registra la URL probada, el ambiente, el navegador y la suite ([run 43159181319](https://github.com/Nachopacca24/Data_science_final/actions/runs/43159181319)).
- En la demostración intencional #15, integración pasó y la suite E2E falló; prod se omitió. No hay evidencia de recepción de correo. Los secretos SMTP faltantes constan en la corrida #18.

## IA-6 · Probar el presupuesto inválido sin escribir texto (JuanDa)

**Sugerencia.** La IA propuso primero probar un presupuesto `"abc"`. Al revisar `recomendaciones.html`, vio que el campo es `type="number"`, donde Playwright no permite escribir texto, y que el JS valida `presupuesto > 0` antes de llamar a la API. Propuso probar solo `0` y `-50` en la pantalla y dejar los tipos inválidos a la capa de integración (DECISIONES A7). También cambió el caso "no alcanza" de Q1 a Q0.01, porque VL-02 de `CASOS.md` ya documenta que con ese presupuesto la lista queda vacía.

**Decisión.** Se aceptó (DECISIONES E6).

**Comprobación.**
- `test_presupuesto_invalido_muestra_error_y_no_lista[0]` y `[-50]`.
- `test_presupuesto_insuficiente_avisa_que_no_alcanza` (Q0.01, lista vacía, restante Q0.01).
- La corrida #17 ([run 43159181319](https://github.com/Nachopacca24/Data_science_final/actions/runs/43159181319)) ejecutó 6 pruebas E2E de regresión exitosas en dev y 2 E2E smoke exitosas en prod. No acredita una selección manual de `suite=smoke` para dev.
- En la corrida #15 fallaron `test_lista_completa_dentro_del_presupuesto` (tarjetas ocultas) y `test_presupuesto_insuficiente_avisa_que_no_alcanza` (mensaje oculto); las otras cuatro E2E pasaron. Resultado: `2 failed, 4 passed in 13.27s` (Python 3.12.16, Chromium), versión `810d14c`. El artefacto `reporte-integracion-dev` contiene `reportes/e2e-dev.xml` y capturas. Fue una demostración intencional independiente: integración pasó y prod se omitió.

## Lo que la IA hizo mal y se corrigió

Para que conste que las sugerencias se revisaron y no se aceptaron a ciegas:
- La primera versión de la pantalla dejaba la lista anterior visible al lado de un mensaje de error. Se encontró al probar la pantalla en el navegador y se corrigió: ahora la lista se oculta.
- La primera versión de la API no arrancaba: el formato de `responses` estaba mal. Se encontró al levantarla y se corrigió antes del primer commit.
- La primera propuesta de las e2e las ponía en un job aparte de `pipeline.yml`, que no habría alcanzado la instancia desplegada. Se corrigió al leer `desplegar.yml` (IA-5).
- El primer parche de los workflows convirtió sus finales de línea de CRLF a LF, y Git habría marcado todas las líneas como cambiadas. Se detectó al revisar el diff y se rehízo para que solo cambien las líneas nuevas.
- Las pruebas e2e se escribieron sin poder abrir un navegador, así que la IA no pudo comprobarlas. Se corrieron en local antes del primer commit.
