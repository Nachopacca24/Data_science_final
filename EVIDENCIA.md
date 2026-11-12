# Evidencia

Qué se corrió, cuándo y qué salió. Solo se registran resultados reales; los estados no ejecutados o no verificables se indican explícitamente.

## 1. Corridas del pipeline en GitHub Actions

Se agregan aquí a medida que corren. Pestaña *Actions* del repo, workflow `pipeline`.

| Fecha | Rama · SHA | lint | unitarias | build | dev | prod | correo | Enlace |
|---|---|---|---|---|---|---|---|---|
| 2026-11-10 01:40 UTC | `calidad_final` · `6edb8ec` | ✅ 19 s | ✅ 15 s | ✅ 19 s | ✅ 25 s | ✅ 20 s | — (no hubo falla) | [run 42737504756](https://github.com/Nachopacca24/Data_science_final/actions/runs/42737504756) |
| 2026-11-10 | `calidad_final` · `f8952fb`¹ | ✅ 14 s | ✅ 17 s | ✅ 19 s | ✅ 23 s | ✅ 25 s | — (no hubo falla) | [run 42741136300](https://github.com/Nachopacca24/Data_science_final/actions/runs/42741136300) |
| 2026-11-10 | `demo-rompe-unitarias` · `d1b4dc4` | ✅ 18 s | ❌ 24 s | ⏭ no corre | ⏭ no corre | ⏭ no corre | ❌ faltan secretos | [run 42741165796](https://github.com/Nachopacca24/Data_science_final/actions/runs/42741165796) |
| 2026-11-11 | `demo-rompe-e2e` · `810d14c` | ✅ | ✅ | ✅ | ✅ integración pasa; ❌ E2E regresión falla | ⏭ no corre | ❌ faltan secretos | No se dispone del enlace de esta corrida |
| No indicada | `calidad_final` · `10837c8` | ✅ | ✅ | ✅ | ✅ 59 integración + 6 E2E (regresión) | ✅ 3 integración + 2 E2E (smoke) | — (no hubo falla) | [run 43159181319](https://github.com/Nachopacca24/Data_science_final/actions/runs/43159181319) |
| 2026-11-11 | `demo-rompe-integracion` · `c77f931` | ✅ | ✅ | ✅ | ❌ integración: 58 pasaron, 1 falló; E2E no se ejecutó | ⏭ no corre | ❌ faltan secretos SMTP | [run 43166417928 (#18)](https://github.com/Nachopacca24/Data_science_final/actions/runs/43166417928) · 1 min 10 s |

La corrida #17 duró 2 min 34 s y usó Chromium. El registro E2E identifica la URL probada, el ambiente, el navegador y la suite.

### Evidencia de ejecución manual con `suite=smoke`

La documentación disponible no acredita una ejecución manual desde Actions → `pipeline` → `Run workflow` seleccionando `suite=smoke` para dev. La corrida #17 acredita regresión en dev y smoke en prod; como prod usa smoke por configuración, ese resultado no demuestra que se haya seleccionado smoke manualmente para dev. Para acreditar esa actividad se requiere el enlace de la corrida manual y sus resultados de integración y E2E en dev.

¹ Después de esa corrida se le cambió el título a ese commit. El contenido es idéntico, pero ahora es `8dbd20d`, "docs(ia): documenta sugerencias de IA (mías)".

### Demo: el código se rompe y las pruebas unitarias detienen el build

La rama `demo-rompe-unitarias` cambia **solo el código**, no las pruebas. En `web/api/esquemas.py`, `Field(gt=0, …)` pasa a `Field(ge=0, …)`: la API acepta un presupuesto de Q0, que el contrato prohíbe.

| Etapa | Resultado |
|---|---|
| lint | ✅ el código es válido; el error es de lógica, no de estilo |
| pruebas-unitarias | ❌ `FAILED tests/unitarias/test_entrada_api.py::test_presupuesto_invalido[0-cero] - AssertionError: {"presupuesto":0.0,"juegos":[],"total_gtq":0.0,"restante_gtq":0.0}` → `1 failed, 86 passed` |
| build, dev, prod | ⏭ no corren: la versión rota nunca se construye ni se despliega |
| correo | ❌ intentó avisar, pero `No se pudo enviar el correo: faltan los secretos SMTP_USUARIO, SMTP_CONTRASENA o CORREO_DESTINO.` Esta rama nunca se une a `calidad_final`. |

#### Corrida verde anterior: 42737504756 · commit `6edb8ec`

| Etapa | Salida |
|---|---|
| pruebas-unitarias | `87 passed` (Python 3.12.16). Hay 1 aviso de la librería: Starlette sugiere `httpx2`; no afecta |
| build | artefacto `imagen-6edb8ec5fd2022bf90eda0ea0d7cf0dfaee3caf6` |
| dev | `OK: http://localhost:8001 responde version=6edb8ec5fd2022bf90eda0ea0d7cf0dfaee3caf6 ambiente=dev` → `34 passed` (regresión) |
| prod | `OK: http://localhost:8002 responde version=6edb8ec5fd2022bf90eda0ea0d7cf0dfaee3caf6 ambiente=prod` → `3 passed, 31 deselected` (smoke) |

Artefactos de la corrida: `imagen-<sha>`, `reporte-unitarias`, `reporte-integracion-dev` y `reporte-integracion-prod` (JUnit XML).

### Demo: el código se rompe y las pruebas e2e detectan el error

La rama `demo-rompe-e2e` cambia **solo el código**, no las pruebas. En `web/pantallas/recomendaciones.js`, `$("resultado").hidden = false` pasa a `$("resultado").hidden = true`: después de recibir la respuesta de la API, la pantalla oculta toda la sección de resultados aunque la respuesta sea correcta. Se lanzó con los valores por defecto (suite regresión, navegador chromium).

| Etapa | Resultado |
|---|---|
| lint | ✅ el código es válido; no hay errores de estilo |
| pruebas-unitarias | ✅ pasan: las unitarias no prueban el JS de la pantalla |
| build | ✅ la imagen se construye correctamente |
| dev | ❌ la integración pasa y las e2e de regresión fallan |
| prod | ⏭ no corre: dev falla y se detiene el despliegue |
| correo | ❌ intentó avisar, pero faltan los secretos `SMTP_USUARIO`, `SMTP_CONTRASENA` y `CORREO_DESTINO` |

La integración de dev pasó, pero la suite E2E de regresión detectó problemas en la pantalla:

| Prueba E2E | Resultado |
|---|---|
| `test_lista_completa_dentro_del_presupuesto` | ❌ Las tarjetas `#lista > li` existen, pero están ocultas. |
| `test_pie_muestra_version_y_ambiente_del_despliegue` | ✅ PASSED |
| `test_presupuesto_invalido_muestra_error_y_no_lista[0]` | ✅ PASSED |
| `test_presupuesto_invalido_muestra_error_y_no_lista[-50]` | ✅ PASSED |
| `test_presupuesto_insuficiente_avisa_que_no_alcanza` | ❌ El mensaje `#vacia` existe, pero está oculto. |
| `test_enviar_sin_favoritos_pide_elegir_uno` | ✅ PASSED |

Resultado: `2 failed, 4 passed in 13.27s` (Python 3.12.16, Chromium). La versión probada fue `810d14c` (`versión 810d14c · dev`). El artefacto `reporte-integracion-dev` contiene `reportes/e2e-dev.xml` y las capturas de los fallos. El enlace de la corrida no está disponible en la evidencia revisada.

La corrida #15 demuestra que E2E puede detectar un problema que no detectó integración. Es una demostración intencional independiente; no forma parte del pipeline normal de `calidad_final`.

### Demo: la integración detecta un error funcional

La corrida #18 corresponde a la rama `demo-rompe-integracion`, commit `c77f931`, y duró 1 min 10 s. El commit parte de `10837c8` (`calidad_final`); su diff cambia únicamente el cálculo de `restante_gtq` en `web/api/main.py`, de `(presupuesto - total) / 100` a `(presupuesto + total) / 100`, sin modificar pruebas.

| Etapa | Resultado |
|---|---|
| lint | ✅ exitoso |
| pruebas unitarias | ✅ exitosas |
| build | ✅ exitoso |
| dev | ❌ 59 pruebas de integración recopiladas: 58 pasaron y 1 falló |
| prod | ⏭ omitido porque dev falló |
| correo | ❌ falló por falta de `SMTP_USUARIO`, `SMTP_CONTRASENA` y `CORREO_DESTINO` |

La prueba que detectó el error fue `test_restante_es_presupuesto_menos_total`: obtuvo Q522.88 y esperaba Q77.12. E2E no se ejecutó porque falló integración. El fallo del correo es independiente de las pruebas y no afecta la validez de esta demostración.

La corrida #18 demuestra que integración detecta un error funcional que pasó las pruebas unitarias. Es una demostración intencional independiente; no forma parte del pipeline normal de `calidad_final`. [run 43166417928](https://github.com/Nachopacca24/Data_science_final/actions/runs/43166417928)

Esta rama no se une a `main` ni a `calidad_final`; demuestra que las pruebas de integración detectan errores funcionales en la API.

La corrida #17 es el pipeline normal exitoso. Las ramas `demo-rompe-e2e` (#15) y `demo-rompe-integracion` (#18) son demostraciones intencionales de fallos y se mantienen separadas de ese resultado.

## 2. Verificación local · 2026-11-09

Se corrió en una Mac con Python 3.14.7 y Docker 28.3.2. Fue sobre `calidad_final` en `945e292`, con los cambios del pipeline todavía sin commit. El pipeline usa Python 3.12, que es el de la imagen.

### Lint

| Herramienta | Alcance | Resultado |
|---|---|---|
| `ruff check .` | `web/`, `ci/`, `tests/unitarias/` | All checks passed |
| `actionlint` 1.7.12 | `.github/workflows/*.yml` | sin errores |

### Pruebas unitarias: 87 pasan (0.6 s)

| Archivo | Pruebas | Qué cubre |
|---|---|---|
| `test_entrada_api.py` | 48 | validación de entrada (presupuesto, favoritos, cuerpo, appid, búsqueda), formato de errores, `/salud`, `/version`, pantalla |
| `test_recomendador.py` | 19 | similitud, las 3 reglas de candidato, mochila (incluye comparación contra la fuerza bruta y el precio justo/un centavo menos) |
| `test_catalogo_y_config.py` | 15 | catálogo dañado no carga, versión por variable/archivo/`local`, ambientes válidos e inválidos |
| `test_verificar_despliegue.py` | 5 | SHA o ambiente distinto detienen el pipeline, API que no responde agota la espera |

**¿Las pruebas detectan errores de verdad?** Se metieron fallas a propósito en el código, una a la vez, y se revirtieron:

| Falla inyectada | Resultado |
|---|---|
| Aceptar presupuesto = 0 (`gt=0` → `ge=0`) | 1 prueba falla ✔ |
| Un juego que cuesta justo el presupuesto ya no cabe (`<=` → `<`) | 3 pruebas fallan ✔ |
| Recomendar juegos que no pasan el umbral | 1 prueba falla ✔ |

### Build único y despliegue en dos ambientes (simulación local del pipeline)

```
docker build -f web/Dockerfile --build-arg APP_VERSION=945e292fff2a… -t recomendador:945e292fff2a… .
```

| Paso | Resultado |
|---|---|
| Build con SHA | imagen de 49 MB, `org.opencontainers.image.revision` = SHA, usuario `app` (no root) |
| Build **sin** SHA | se niega a construir ✔ |
| dev (`:8001`, `APP_AMBIENTE=dev`) | `OK: version=945e292fff2aa1b793fb833e3bbd0f015463afea ambiente=dev` |
| Integración en dev (regresión) | **34 pasan** (0.17 s) |
| prod (`:8002`, misma imagen, `APP_AMBIENTE=prod`) | `OK: version=945e292fff2aa1b793fb833e3bbd0f015463afea ambiente=prod` |
| Integración en prod (smoke) | **3 pasan**, 31 no seleccionadas |
| Healthcheck del contenedor | `healthy` |
| Peor caso: Q10,000 con 5 favoritos | 18 ms |

**La verificación de versión detiene lo que debe detener:**

| Caso | Salida | Código |
|---|---|---|
| Instancia de prod verificada como dev | `FALLA: ambiente es 'prod' y se esperaba 'dev'` | 1 |
| SHA distinto al del build | `FALLA: version es '945e292…' y se esperaba 'deadbeef'` | 1 |
| API que no levanta | `FALLA: …/salud no respondió 'ok' en 3 s (… Connection refused)` | 1 |
| Contenedor con `APP_AMBIENTE=produccion` | la API no arranca | 3 |

### Pantalla

Se probó en un navegador real (Playwright) a 1200 px y a 375 px de ancho, con este flujo: buscar "doom", elegir DOOM, elegir Hades y recomendar con Q300. Salió la misma lista que la API (DOOM Eternal, Risk of Rain, Half-Life 2, Hotline Miami y The Binding of Isaac, por un total de Q287.88). Con un presupuesto de `300.555` muestra el error `presupuesto: admite como máximo 2 decimales (centavos)` y oculta la lista anterior. La consola no muestra más errores que ese 422, que es el esperado.

## Cómo reproducir

```bash
pip install -r web/requirements-dev.txt
ruff check . && pytest
SHA=$(git rev-parse HEAD)
docker build -f web/Dockerfile --build-arg APP_VERSION=$SHA -t recomendador:$SHA .
docker run -d --name recomendador-dev -p 8001:8000 -e APP_AMBIENTE=dev recomendador:$SHA
python ci/verificar_despliegue.py --url http://localhost:8001 --sha $SHA --ambiente dev
API_URL=http://localhost:8001 pytest tests/integracion
```

## 3. Cierre de entrega: evidencia disponible

La documentación y las referencias locales revisadas no acreditan las siguientes actividades. Los requisitos indicados describen qué evidencia permitiría verificarlas; no implican que ya se hayan realizado.

| Actividad | Estado verificable | Evidencia necesaria para acreditarla |
|---|---|---|
| Pull request de `calidad_final` hacia `main` | No acreditado en los documentos ni en las referencias locales revisadas | Enlace al PR que muestre la rama de origen y `main` como destino |
| Pipeline de ese PR con prod omitido | El workflow configura que prod no corra en eventos `pull_request`; no se identificó una corrida de PR concreta | Enlace a la corrida del PR con el job prod omitido |
| Merge del PR | No acreditado en los documentos ni en las referencias locales revisadas | Estado de PR que muestre el merge o su commit de merge |
| Pipeline exitoso en `main` | No se identificó una corrida exitosa en `main` | Enlace a la corrida exitosa en la rama `main` |
| Tag `entrega-calidad` | No aparece en las etiquetas locales ni en los documentos revisados | Tag y SHA al que apunta |
| Envío del SHA a MIU | No acreditado en los documentos revisados | Registro del envío y SHA comunicado |
