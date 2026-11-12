# Evidencia

Qué se corrió, cuándo y qué salió. Solo resultados reales: lo que todavía no se ha corrido dice **pendiente**.

## 1. Corridas del pipeline en GitHub Actions

Se agregan aquí a medida que corren. Pestaña *Actions* del repo, workflow `pipeline`.

| Fecha | Rama · SHA | lint | unitarias | build | dev | prod | correo | Enlace |
|---|---|---|---|---|---|---|---|---|
| 2026-11-10 01:40 UTC | `calidad_final` · `6edb8ec` | ✅ 19 s | ✅ 15 s | ✅ 19 s | ✅ 25 s | ✅ 20 s | — (no hubo falla) | [run 42737504756](https://github.com/Nachopacca24/Data_science_final/actions/runs/42737504756) |
| 2026-11-10 | `calidad_final` · `f8952fb`¹ | ✅ 14 s | ✅ 17 s | ✅ 19 s | ✅ 23 s | ✅ 25 s | — (no hubo falla) | [run 42741136300](https://github.com/Nachopacca24/Data_science_final/actions/runs/42741136300) |
| 2026-11-10 | `demo-rompe-unitarias` · `d1b4dc4` | ✅ 18 s | ❌ 24 s | ⏭ no corre | ⏭ no corre | ⏭ no corre | ❌ faltan secretos | [run 42741165796](https://github.com/Nachopacca24/Data_science_final/actions/runs/42741165796) |
| 2026-11-11 | `demo-rompe-e2e` · `810d14c` | ✅ COMPLETAR s | ✅ COMPLETAR s | ✅ COMPLETAR s | ❌ e2e COMPLETAR s | ⏭ no corre | ❌ faltan secretos | [run COMPLETAR](COMPLETAR enlace) |

¹ Después de esa corrida se le cambió el título a ese commit. El contenido es idéntico, pero ahora es `8dbd20d`, "docs(ia): documenta sugerencias de IA (mías)".

### Demo: el código se rompe y las pruebas unitarias detienen el build

La rama `demo-rompe-unitarias` cambia **solo el código**, no las pruebas. En `web/api/esquemas.py`, `Field(gt=0, …)` pasa a `Field(ge=0, …)`: la API acepta un presupuesto de Q0, que el contrato prohíbe.

| Etapa | Resultado |
|---|---|
| lint | ✅ el código es válido; el error es de lógica, no de estilo |
| pruebas-unitarias | ❌ `FAILED tests/unitarias/test_entrada_api.py::test_presupuesto_invalido[0-cero] - AssertionError: {"presupuesto":0.0,"juegos":[],"total_gtq":0.0,"restante_gtq":0.0}` → `1 failed, 86 passed` |
| build, dev, prod | ⏭ no corren: la versión rota nunca se construye ni se despliega |
| correo | ❌ intentó avisar, pero `No se pudo enviar el correo: faltan los secretos SMTP_USUARIO, SMTP_CONTRASENA o CORREO_DESTINO.` Esta rama nunca se une a `calidad_final`. |

Detalle de esa corrida (sacado de los logs):

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
| dev | ❌ la integración pasa (34) y las e2e fallan: 2 fallan y 4 pasan |
| prod | ⏭ no corre: dev falla y se detiene el despliegue |
| correo | ❌ intentó avisar, pero faltan los secretos `SMTP_USUARIO`, `SMTP_CONTRASENA` y `CORREO_DESTINO` |

Detalle de esa corrida (sacado de los logs):

| Prueba e2e | Salida |
|---|---|
| `test_lista_completa_dentro_del_presupuesto` | ❌ `FAILED`: las tarjetas `#lista > li` existen, pero están ocultas |
| `test_pie_muestra_version_y_ambiente_del_despliegue` | ✅ `PASSED` |
| `test_presupuesto_invalido_muestra_error_y_no_lista[0]` | ✅ `PASSED` |
| `test_presupuesto_invalido_muestra_error_y_no_lista[-50]` | ✅ `PASSED` |
| `test_presupuesto_insuficiente_avisa_que_no_alcanza` | ❌ `FAILED`: el mensaje `#vacia` existe, pero está oculto |
| `test_enviar_sin_favoritos_pide_elegir_uno` | ✅ `PASSED` |

Resultado final: `2 failed, 4 passed in 13.27s` (Python 3.12.16, Chromium). La versión probada fue `810d14c` (`versión 810d14c · dev`): las pruebas detectaron que la pantalla no muestra los resultados, aunque la API responde bien.

Artefacto de la corrida: `reporte-integracion-dev`, que incluye `reportes/e2e-dev.xml` (JUnit XML) y las capturas de lo que falló. Corrida: [COMPLETAR enlace].

Esta rama no se une a `main` ni a `calidad_final`; se conserva solo para demostrar que las pruebas e2e detectan errores en la capa de presentación.

Por probar en GitHub:
- [x] Corrida completa en verde (push a `calidad_final`).
- [ ] Corrida a mano con `suite = smoke`.
- [x] Una falla a propósito pone el build en rojo y detiene el despliegue (`demo-rompe-unitarias`).
- [x] Una falla en las pruebas e2e detiene el despliegue (`demo-rompe-e2e`).
- [ ] El correo de esa falla llega (pendiente: el dueño del repo tiene que agregar los secretos `SMTP_*`; ver README).
- [ ] En un pull request, prod se salta.

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